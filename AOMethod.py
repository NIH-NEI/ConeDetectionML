import multiprocessing as mp
import numbers
import os

import numpy as np
import scipy.cluster.hierarchy as hcluster
import SimpleITK as sitk
import tensorflow as tf
from skimage.transform import resize

from AONetwork import UNet


# Replace the old tf.ConfigProto/tf.Session block. TF2 uses eager execution by default.
core_num = mp.cpu_count()
tf.config.threading.set_inter_op_parallelism_threads(core_num)
tf.config.threading.set_intra_op_parallelism_threads(core_num)
for gpu in tf.config.list_physical_devices("GPU"):
    try:
        tf.config.experimental.set_memory_growth(gpu, True)
    except RuntimeError:
        # Memory growth must be set before GPU initialization; ignore if already initialized.
        pass

training_img_rows = 256
training_img_cols = 256
training_img_mean = 127.68837
training_img_std = 30.03274

scanning_resolution = {
    "large": [333, 333],
    "small": [128, 128],
}


class ao_method:
    def __init__(self):
        self._cone_detection_model = None
        self._scanning_size = None

    def create_unet_model(self, training_size, output_class):
        if isinstance(training_size, numbers.Number):
            training_size = (int(training_size), int(training_size))

        model = UNet(input_shape=(training_size[0], training_size[1], 1), output_class=output_class)
        model.summary()
        return model

    def create_detection_model(self, model_name, model_weight_path):
        if not os.path.isfile(model_weight_path):
            raise ValueError(f"could not load weight {model_weight_path}")

        self._scanning_size = scanning_resolution["small"] if "small" in model_name.lower() else scanning_resolution["large"]

        self._cone_detection_model = self.create_unet_model(
            training_size=(training_img_rows, training_img_cols),
            output_class=1,
        )
        self._cone_detection_model.load_weights(model_weight_path)

    def preprocess_images(self, img):
        input_img_size = img.GetSize()
        img_arr = sitk.GetArrayFromImage(img)

        if input_img_size[1] > self._scanning_size[0] and input_img_size[0] > self._scanning_size[1]:
            row_subdivision = int(np.ceil(input_img_size[1] / self._scanning_size[0]))
            col_subdivision = int(np.ceil(input_img_size[0] / self._scanning_size[1]))
            num_of_sub_imgs = row_subdivision * col_subdivision
            normalized_imgs = np.zeros((num_of_sub_imgs, training_img_rows, training_img_cols), dtype=np.float32)

            for i in range(row_subdivision):
                if i == row_subdivision - 1 and i * self._scanning_size[0] < input_img_size[1]:
                    row_indices = (input_img_size[1] - self._scanning_size[0], input_img_size[1])
                else:
                    row_indices = (i * self._scanning_size[0], (i + 1) * self._scanning_size[0])

                for j in range(col_subdivision):
                    if j == col_subdivision - 1 and j * self._scanning_size[1] < input_img_size[0]:
                        col_indices = (input_img_size[0] - self._scanning_size[1], input_img_size[0])
                    else:
                        col_indices = (j * self._scanning_size[1], (j + 1) * self._scanning_size[1])

                    sub_img = img_arr[row_indices[0] : row_indices[1], col_indices[0] : col_indices[1]]
                    sub_img = resize(sub_img, (training_img_rows, training_img_cols), preserve_range=True)
                    sub_img = sub_img.astype(np.float32)
                    sub_img -= training_img_mean
                    sub_img /= training_img_std
                    normalized_imgs[j + i * col_subdivision] = sub_img
        else:
            normalized_imgs = np.zeros((1, training_img_rows, training_img_cols), dtype=np.float32)
            sub_img = resize(img_arr, (training_img_rows, training_img_cols), preserve_range=True)
            sub_img = sub_img.astype(np.float32)
            sub_img -= training_img_mean
            sub_img /= training_img_std
            normalized_imgs[0] = sub_img

        return normalized_imgs[..., np.newaxis]

    def compute_probability_map(self, img, normalized_imgs):
        input_img_size = img.GetSize()
        res_imgs = self._cone_detection_model.predict(normalized_imgs, verbose=0)

        if res_imgs.shape[-1] == 1:
            res_imgs = np.squeeze(res_imgs, axis=-1)
        else:
            res_imgs = res_imgs[..., 0]

        if res_imgs.shape[0] == 1:
            res_imgs = np.squeeze(res_imgs, axis=0)
            prob_img = resize(res_imgs, (input_img_size[1], input_img_size[0]), preserve_range=True)
        else:
            prob_img = np.zeros((input_img_size[1], input_img_size[0]), dtype=np.float32)
            row_subdivision = int(np.ceil(input_img_size[1] / self._scanning_size[0]))
            col_subdivision = int(np.ceil(input_img_size[0] / self._scanning_size[1]))

            for i in range(row_subdivision):
                if i == row_subdivision - 1 and i * self._scanning_size[0] < input_img_size[1]:
                    row_indices = (input_img_size[1] - self._scanning_size[0], input_img_size[1])
                else:
                    row_indices = (i * self._scanning_size[0], (i + 1) * self._scanning_size[0])

                for j in range(col_subdivision):
                    if j == col_subdivision - 1 and j * self._scanning_size[1] < input_img_size[0]:
                        col_indices = (input_img_size[0] - self._scanning_size[1], input_img_size[0])
                    else:
                        col_indices = (j * self._scanning_size[1], (j + 1) * self._scanning_size[1])

                    sub_res_img = res_imgs[j + i * col_subdivision]
                    sub_res_img = resize(
                        sub_res_img,
                        (self._scanning_size[0], self._scanning_size[1]),
                        preserve_range=True,
                    )
                    prob_img[row_indices[0] : row_indices[1], col_indices[0] : col_indices[1]] = sub_res_img

        return prob_img

    # Backward-compatible misspelled alias used by the original code.
    def compute_probablity_map(self, img, normalized_imgs):
        return self.compute_probability_map(img, normalized_imgs)

    def postprocess_probability_map(self, img_origin, fov_ratio, prob_img, prob_value, distance_value):
        res_img = np.zeros(prob_img.shape, dtype=np.uint8)
        res_img[prob_img > prob_value] = 1

        dist_img = sitk.SignedMaurerDistanceMap(
            sitk.GetImageFromArray(res_img),
            insideIsPositive=True,
            squaredDistance=False,
            useImageSpacing=False,
        )

        dist_s_img = sitk.SmoothingRecursiveGaussian(dist_img, 1.0, True)
        dist_s_arr = sitk.GetArrayFromImage(dist_s_img)
        dist_s_arr[dist_s_arr < 0] = 0
        dist_s_img = sitk.GetImageFromArray(dist_s_arr)

        peak_filter = sitk.RegionalMaximaImageFilter()
        peak_filter.SetForegroundValue(1)
        peak_filter.FullyConnectedOn()
        peaks = peak_filter.Execute(dist_s_img)

        stats = sitk.LabelShapeStatisticsImageFilter()
        stats.Execute(sitk.ConnectedComponent(peaks))
        detection_centroids = [stats.GetCentroid(label) for label in stats.GetLabels()]

        detection_res = []
        if len(detection_centroids) > 10:
            clusters = hcluster.fclusterdata(detection_centroids, distance_value, criterion="distance")
            np_detection_centroids = np.asarray(detection_centroids)
            for cluster_id in range(np.amin(clusters), np.amax(clusters) + 1):
                pts = np_detection_centroids[np.where(clusters == cluster_id)]
                xpos = float(np.mean(pts[:, 0]))
                ypos = float(np.mean(pts[:, 1]))

                xpos = img_origin[0] + (xpos - img_origin[0]) / fov_ratio
                ypos = img_origin[1] + (ypos - img_origin[1]) / fov_ratio
                detection_res.append((xpos, ypos))

        return detection_res

    def detect_cones(self, img, fov, prob_value, distance_value):
        if self._cone_detection_model is None:
            return None

        fov_ratio = fov / 0.75
        euler2d = sitk.Euler2DTransform()
        euler2d.SetCenter(img.TransformContinuousIndexToPhysicalPoint(np.array(img.GetSize()) / 2.0))
        euler2d.SetTranslation((0, 0))

        output_spacing = (img.GetSpacing()[0] / fov_ratio, img.GetSpacing()[1] / fov_ratio)
        output_origin = img.GetOrigin()
        output_direction = img.GetDirection()
        output_size = [int(img.GetSize()[0] * fov_ratio + 0.5), int(img.GetSize()[1] * fov_ratio + 0.5)]

        img = sitk.Resample(
            img,
            output_size,
            euler2d,
            sitk.sitkLinear,
            output_origin,
            output_spacing,
            output_direction,
        )

        normalized_imgs = self.preprocess_images(img)
        prob_img = self.compute_probability_map(img, normalized_imgs)
        return self.postprocess_probability_map(output_origin, fov_ratio, prob_img, prob_value, distance_value)

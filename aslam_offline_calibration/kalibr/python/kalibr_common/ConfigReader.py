import yaml
import sys
import numpy as np
import functools

import math
import aslam_cv as cv
import aslam_cv_backend as cvb
import sm


class AslamCamera(object):
    def __init__(self, camera_model, intrinsics, dist_model, dist_coeff, resolution):
        # setup the aslam camera
        if camera_model == 'pinhole':
            focalLength = intrinsics[0:2]
            principalPoint = intrinsics[2:4]

            if dist_model == 'radtan':
                dist = cv.RadialTangentialDistortion(dist_coeff[0], dist_coeff[1],
                                                     dist_coeff[2], dist_coeff[3])

                proj = cv.DistortedPinholeProjection(focalLength[0], focalLength[1],
                                                     principalPoint[0], principalPoint[1],
                                                     resolution[0], resolution[1],
                                                     dist)

                self.geometry = cv.DistortedPinholeCameraGeometry(proj)

                self.frameType = cv.DistortedPinholeFrame
                self.keypointType = cv.Keypoint2
                self.reprojectionErrorType = cvb.DistortedPinholeReprojectionErrorSimple
                self.undistorterType = cv.PinholeUndistorterNoMask

            elif dist_model == 'equidistant':
                dist = cv.EquidistantDistortion(dist_coeff[0], dist_coeff[1], dist_coeff[2], dist_coeff[3])

                proj = cv.EquidistantPinholeProjection(focalLength[0], focalLength[1],
                                                       principalPoint[0], principalPoint[1],
                                                       resolution[0], resolution[1],
                                                       dist)

                self.geometry = cv.EquidistantDistortedPinholeCameraGeometry(proj)

                self.frameType = cv.EquidistantDistortedPinholeFrame
                self.keypointType = cv.Keypoint2
                self.reprojectionErrorType = cvb.EquidistantDistortedPinholeReprojectionErrorSimple
                self.undistorterType = cv.EquidistantPinholeUndistorterNoMask

            elif dist_model == 'fov':
                dist = cv.FovDistortion(dist_coeff[0])

                proj = cv.FovPinholeProjection(focalLength[0], focalLength[1],
                                               principalPoint[0], principalPoint[1],
                                               resolution[0], resolution[1], dist)

                self.geometry = cv.FovDistortedPinholeCameraGeometry(proj)

                self.frameType = cv.FovDistortedPinholeFrame
                self.keypointType = cv.Keypoint2
                self.reprojectionErrorType = cvb.FovDistortedPinholeReprojectionErrorSimple
                self.undistorterType = cv.FovPinholeUndistorterNoMask
            elif dist_model == 'none':
                proj = cv.PinholeProjection(focalLength[0], focalLength[1],
                                            principalPoint[0], principalPoint[1],
                                            resolution[0], resolution[1])

                self.camera = cv.PinholeCameraGeometry(proj)

                self.frameType = cv.PinholeFrame
                self.keypointType = cv.Keypoint2
                self.reprojectionErrorType = cvb.PinholeReprojectionErrorSimple
            else:
                self.raiseError("pinhole camera model does not support distortion model '{}'".format(dist_model))

        elif camera_model == 'omni':
            xi_omni = intrinsics[0]
            focalLength = intrinsics[1:3]
            principalPoint = intrinsics[3:5]

            if dist_model == 'radtan':
                dist = cv.RadialTangentialDistortion(dist_coeff[0], dist_coeff[1],
                                                     dist_coeff[2], dist_coeff[3])

                proj = cv.DistortedOmniProjection(xi_omni, focalLength[0], focalLength[1],
                                                  principalPoint[0], principalPoint[1],
                                                  resolution[0], resolution[1],
                                                  dist)

                self.geometry = cv.DistortedOmniCameraGeometry(proj)

                self.frameType = cv.DistortedOmniFrame
                self.keypointType = cv.Keypoint2
                self.reprojectionErrorType = cvb.DistortedOmniReprojectionErrorSimple
                self.undistorterType = cv.OmniUndistorterNoMask

            elif dist_model == 'equidistant':

                raise RuntimeError("Omni with equidistant model not yet supported!")

                dist = cv.EquidistantPinholeProjection(dist_coeff[0], dist_coeff[1],
                                                       dist_coeff[2], dist_coeff[3])

                proj = cv.EquidistantOmniProjection(xi_omni, focalLength[0], focalLength[1],
                                                    principalPoint[0], principalPoint[1],
                                                    resolution[0], resolution[1],
                                                    dist)

                self.geometry = cv.EquidistantDistortedOmniCameraGeometry(proj)

                self.frameType = cv.DistortedOmniFrame
                self.keypointType = cv.Keypoint2
                self.reprojectionErrorType = cvb.EquidistantDistortedOmniReprojectionErrorSimple

            elif dist_model == 'none':

                proj = cv.OmniProjection(xi_omni, focalLength[0], focalLength[1],
                                         principalPoint[0], principalPoint[1],
                                         resolution[0], resolution[1])

                self.geometry = cv.OmniCameraGeometry(proj)

                self.frameType = cv.OmniFrame
                self.keypointType = cv.Keypoint2
                self.reprojectionErrorType = cvb.OmniReprojectionErrorSimple

            else:
                raise RuntimeError("omni camera model does not support distortion model '{}'".format(dist_model))

        elif camera_model == 'eucm':
            alpha_uni = intrinsics[0]
            beta_uni = intrinsics[1]
            focalLength = intrinsics[2:4]
            principalPoint = intrinsics[4:6]

            if dist_model == 'none':
                proj = cv.ExtendedUnifiedProjection(alpha_uni, beta_uni, focalLength[0], focalLength[1],
                                                    principalPoint[0], principalPoint[1],
                                                    resolution[0], resolution[1])

                self.geometry = cv.ExtendedUnifiedCameraGeometry(proj)

                self.frameType = cv.ExtendedUnifiedFrame
                self.keypointType = cv.Keypoint2
                self.reprojectionErrorType = cvb.ExtendedUnifiedReprojectionErrorSimple

            else:
                raise RuntimeError(
                    "camera model {} does not support distortion model '{}'".format(camera_model, dist_model))

        elif camera_model == 'ds':
            xi_ds = intrinsics[0]
            alpha_ds = intrinsics[1]
            focalLength = intrinsics[2:4]
            principalPoint = intrinsics[4:6]

            if dist_model == 'none':
                proj = cv.DoubleSphereProjection(xi_ds, alpha_ds, focalLength[0], focalLength[1],
                                                 principalPoint[0], principalPoint[1],
                                                 resolution[0], resolution[1])

                self.geometry = cv.DoubleSphereCameraGeometry(proj)

                self.frameType = cv.DoubleSphereFrame
                self.keypointType = cv.Keypoint2
                self.reprojectionErrorType = cvb.DoubleSphereReprojectionErrorSimple
            else:
                raise RuntimeError(
                    "camera model {} does not support distortion model '{}'".format(camera_model, dist_model))

        else:
            raise RuntimeError("Unknown camera model '{}'".format(camera_model))

    @classmethod
    def fromParameters(cls, params):
        # get the data
        camera_model, intrinsics = params.getIntrinsics()
        dist_model, dist_coeff = params.getDistortion()
        resolution = params.getResolution()
        return AslamCamera(camera_model, intrinsics, dist_model, dist_coeff, resolution)


# wrapper to ctach all KeyError exception (field missing in yaml ...)
def catch_keyerror(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except KeyError as e:
            args[0].raiseError("Field {0} missing in file: {1}".format(e, args[0].yamlFile))

    return func


class ParametersBase(object):
    def __init__(self, yamlFile, name, createYaml=False):
        # load the tree
        self.yamlFile = yamlFile
        self.name = name

        # load yaml if we don't create a new one
        if not createYaml:
            self.data = self.readYaml()
        else:
            self.data = dict()

    # load from yaml file
    def readYaml(self):
        try:
            with open(self.yamlFile, 'r') as f:
                data = yaml.safe_load(f)
                f.close()
        except:
            self.raiseError("Could not read configuration from {0}".format(self.yamlFile))

        return data

    # write to yaml file
    def writeYaml(self, filename=None):
        if not filename:
            filename = self.yamlFile  # overwrite source file

        try:
            with open(filename, 'w') as outfile:
                outfile.write(yaml.dump(self.data))
        except:
            self.raiseError("Could not write configuration to {0}".format(self.yamlFile))

    def getYamlDict(self):
        return self.data

    def setYamlDict(self, yamldict):
        self.data = yamldict

    def raiseError(self, message):
        header = "[{0} Reader]: ".format(self.name)
        raise RuntimeError("{0}{1}".format(header, message))

class SensorParametersBase(ParametersBase):
    def __init__(self, yamlFile, name, reference_sensor_name, createYaml=False):
        ParametersBase.__init__(self, yamlFile, name, createYaml)
        self.reference_sensor_name = reference_sensor_name
        self.extrinsics_field_name = "T_here_{0}".format(reference_sensor_name)
        self.timeshift_field_name = "timeshift_to_{0}".format(reference_sensor_name)

    # rostopic
    def checkRosTopic(self, topic):
        if not isinstance(topic, str):
            self.raiseError("rostopic has to be a string")

    @catch_keyerror
    def getRosTopic(self):
        self.checkRosTopic(self.data["rostopic"])
        return self.data["rostopic"]

    def setRosTopic(self, topic):
        self.checkRosTopic(topic)
        self.data["rostopic"] = topic

    def hasExtrinsics(self):
        return self.extrinsics_field_name in self.data

    def setExtrinsicsReferenceToHere(self, extrinsics):
        if not isinstance(extrinsics, sm.Transformation):
            raise RuntimeError("setExtrinsicsReferenceToHere(): provide extrinsics as an sm.Transformation object")

        self.data[self.extrinsics_field_name] = extrinsics.T().tolist()

    @catch_keyerror
    def getExtrinsicsReferenceToHere(self):
        try:
            trafo = sm.Transformation(np.array(self.data[self.extrinsics_field_name]))
            t = trafo.T()  # for error checking
        except:
            self.raiseError("invalid LiDAR extrinsics")
        return trafo

    def checkTimeshiftToReference(self, time_shift):
        if not isinstance(time_shift, float):
            self.raiseError("invalid timeshift in " + self.yamlFile)

    @catch_keyerror
    def getTimeshiftToReference(self):
        return self.data[self.timeshift_field_name]

    def setTimeshiftToReference(self, time_shift):
        self.checkTimeshiftToReference(time_shift)
        self.data[self.timeshift_field_name] = time_shift


class CameraParameters(SensorParametersBase):
    def __init__(self, yamlFile, reference_sensor_name="camera0", createYaml=False):
        SensorParametersBase.__init__(self, yamlFile, "CameraConfig", reference_sensor_name, createYaml)

    ###################################################
    # Accessors
    ###################################################

    # intrinsics
    def checkIntrinsics(self, model, intrinsics):
        cameraModels = ['pinhole',
                        'omni',
                        'eucm',
                        'ds']

        if model not in cameraModels:
            self.raiseError("Unknown camera model '{}'; available models: {}.".format(model, ", ".join(cameraModels)))

        if model == 'pinhole':
            if len(intrinsics) != 4:
                self.raiseError(
                    "invalid intrinsics for pinhole; should be [fu, fv, pu, pv], but got {} parameters".format(
                        len(intrinsics)))

            focalLength = intrinsics[0:2]
            principalPoint = intrinsics[2:4]

        elif model == 'omni':
            if len(intrinsics) != 5:
                self.raiseError(
                    "invalid intrinsics for omni; should be [xi, fu, fv, pu, pv], but got {} parameters".format(
                        len(intrinsics)))

            xi_omni = intrinsics[0]
            focalLength = intrinsics[1:3]
            principalPoint = intrinsics[3:5]

            if xi_omni < 0:
                self.raiseError("invalid xi_omni of {} (xi>0)".format(xi_omni))

        elif model == "ds":

            if len(intrinsics) != 6:
                self.raiseError(
                    "invalid intrinsics for ds; should be [xi, alpha, fu, fv, pu, pv], but got {} parameters".format(
                        len(intrinsics)))

            xi_ds = intrinsics[0]
            alpha_ds = intrinsics[1]
            focalLength = intrinsics[2:4]
            principalPoint = intrinsics[4:6]

            if alpha_ds < 0 or alpha_ds >= 1:
                self.raiseError("invalid alpha_ds of {} (0<=alpha<1)".format(alpha_ds))

        elif model == "eucm":

            if len(intrinsics) != 6:
                self.raiseError(
                    "invalid intrinsics for ds; should be [xi, alpha, fu, fv, pu, pv], but got {} parameters".format(
                        len(intrinsics)))

            alpha_eucm = intrinsics[0]
            beta_eucm = intrinsics[1]
            focalLength = intrinsics[2:4]
            principalPoint = intrinsics[4:6]

            if alpha_eucm < 0 or alpha_eucm >= 1:
                self.raiseError("invalid alpha_eucm of {} (0<=alpha<1)".format(alpha_eucm))

            if beta_eucm < 0:
                self.raiseError("invalid beta_eucm of {} (beta>=0)".format(beta_eucm))

        else:
            self.raiseError('internal error: invalid camera model {} (should have been checked before)'.format(model))

        if not isinstance(focalLength[0], float) or not isinstance(focalLength[1], float) or focalLength[0] < 0.0 or \
                focalLength[1] < 0.0:
            self.raiseError("invalid focalLength (2 floats)")

        if principalPoint[0] < 0.0 or principalPoint[1] < 0.0 or not isinstance(principalPoint[0],
                                                                                float) or not isinstance(
                principalPoint[1], float):
            self.raiseError("invalid principalPoint")

    @catch_keyerror
    def getIntrinsics(self):
        self.checkIntrinsics(self.data["camera_model"],
                             self.data["intrinsics"])

        return self.data["camera_model"], self.data["intrinsics"]

    def setIntrinsics(self, model, intrinsics):
        self.checkIntrinsics(model, intrinsics)

        self.data["camera_model"] = model
        self.data["intrinsics"] = [float(val) for val in intrinsics]

    # distortion
    def checkDistortion(self, model, coeffs):
        distortionModelsAndNumParams = {'radtan': 4,
                                        'equidistant': 4,
                                        'fov': 1,
                                        'none': 0}

        if model not in distortionModelsAndNumParams:
            self.raiseError("Unknown distortion model '{}'. Supported models: {}. )".format(
                model, ", ".join(distortionModelsAndNumParams.keys())))

        if len(coeffs) != distortionModelsAndNumParams[model]:
            self.raiseError("distortion model '{}' requires {} coefficients; {} given".format(
                model, distortionModelsAndNumParams[model], len(coeffs)))

    @catch_keyerror
    def getDistortion(self):
        self.checkDistortion(self.data["distortion_model"],
                             self.data["distortion_coeffs"])
        return self.data["distortion_model"], self.data["distortion_coeffs"]

    def setDistortion(self, model, coeffs):
        self.checkDistortion(model, coeffs)
        self.data["distortion_model"] = model
        self.data["distortion_coeffs"] = [float(val) for val in coeffs]

    # resolution
    def checkResolution(self, resolution):
        if len(resolution) != 2 or not isinstance(resolution[0], int) or not isinstance(resolution[1], int):
            self.raiseError("invalid resolution")

    @catch_keyerror
    def getResolution(self):
        self.checkResolution(self.data["resolution"])
        return self.data["resolution"]

    def setResolution(self, resolution):
        self.checkResolution(resolution)
        self.data["resolution"] = resolution

    ###################################################
    # Helpers
    ###################################################
    def printDetails(self, dest=sys.stdout):
        # get the data
        camera_model, intrinsics = self.getIntrinsics()
        dist_model, dist_coeff = self.getDistortion()
        resolution = self.getResolution()

        if camera_model == 'pinhole':
            focalLength = intrinsics[0:2]
            principalPoint = intrinsics[2:4]

        elif camera_model == 'omni':
            xi_omni = intrinsics[0]
            focalLength = intrinsics[1:3]
            principalPoint = intrinsics[3:5]

        elif camera_model == 'eucm':
            [alpha_eucm, beta_eucm] = intrinsics[0:2]
            focalLength = intrinsics[2:4]
            principalPoint = intrinsics[4:6]

        elif camera_model == 'ds':
            [xi_ds, alpha_ds] = intrinsics[0:2]
            focalLength = intrinsics[2:4]
            principalPoint = intrinsics[4:6]

        else:
            self.raiseError("Unknown camera model '{}'.".format(camera_model))

        print >> dest, "  Camera model: {0}".format(camera_model)
        print >> dest, "  Focal length: {0}".format(focalLength)
        print >> dest, "  Principal point: {0}".format(principalPoint)
        if camera_model == 'omni':
            print >> dest, "  Omni xi: {0}".format(xi_omni)
        if camera_model == 'eucm':
            print >> dest, "  EUCM alpha: {0}".format(alpha_eucm)
            print >> dest, "  EUCM beta: {0}".format(beta_eucm)
        if camera_model == 'ds':
            print >> dest, "  DS xi: {0}".format(xi_ds)
            print >> dest, "  DS alpha: {0}".format(alpha_ds)
        print >> dest, "  Distortion model: {0}".format(dist_model)
        print >> dest, "  Distortion coefficients: {0}".format(dist_coeff)


class ImuParameters(SensorParametersBase):
    def __init__(self, yamlFile, reference_sensor_name="camera0", createYaml=False):
        SensorParametersBase.__init__(self, yamlFile, "ImuConfig", reference_sensor_name, createYaml)

    ###################################################
    # Accessors
    ###################################################
    def checkModel(self, model):
        if not isinstance(model, str):
            self.raiseError("IMU model has to be a string")

    @catch_keyerror
    def getModel(self):
        self.checkModel(self.data["model"])
        return self.data["model"]

    # update rate
    def checkUpdateRate(self, update_rate):
        if update_rate <= 0.0:
            self.raiseError("invalid update_rate")

    @catch_keyerror
    def getUpdateRate(self):
        self.checkUpdateRate(self.data["update_rate"])
        return self.data["update_rate"]

    def setUpdateRate(self, update_rate):
        self.checkUpdateRate(update_rate)
        self.data["update_rate"] = update_rate

    # accelerometer statistics
    def checkAccelerometerStatistics(self, noise_density, random_walk):
        if noise_density <= 0.0:
            self.raiseError("invalid accelerometer_noise_density")
        if random_walk <= 0.0:
            self.raiseError("invalid accelerometer_random_walk")

    @catch_keyerror
    def getAccelerometerStatistics(self):
        self.checkAccelerometerStatistics(self.data["accelerometer_noise_density"],
                                          self.data["accelerometer_random_walk"])
        accelUncertaintyDiscrete = self.data["accelerometer_noise_density"] / math.sqrt(1.0 / self.getUpdateRate())
        return accelUncertaintyDiscrete,\
               self.data["accelerometer_random_walk"],\
               self.data["accelerometer_noise_density"]

    def setAccelerometerStatistics(self, noise_density, random_walk):
        self.checkAccelerometerStatistics(noise_density, random_walk)
        self.data["accelerometer_noise_density"] = noise_density
        self.data["accelerometer_random_walk"] = random_walk

    # gyro statistics
    def checkGyroStatistics(self, noise_density, random_walk):
        if noise_density <= 0.0:
            self.raiseError("invalid gyroscope_noise_density")
        if random_walk <= 0.0:
            self.raiseError("invalid gyroscope_random_walk")

    @catch_keyerror
    def getGyroStatistics(self):
        self.checkGyroStatistics(self.data["gyroscope_noise_density"], self.data["gyroscope_random_walk"])
        gyroUncertaintyDiscrete = self.data["gyroscope_noise_density"] / math.sqrt(1.0 / self.getUpdateRate())
        return gyroUncertaintyDiscrete, self.data["gyroscope_random_walk"], self.data["gyroscope_noise_density"]

    def setGyroStatistics(self, noise_density, random_walk):
        self.checkGyroStatistics(noise_density, random_walk)
        self.data["gyroscope_noise_density"] = noise_density
        self.data["gyroscope_random_walk"] = random_walk

    def formatIndented(self, indent, np_array):
        return indent + str(np.array_str(np_array)).replace('\n', "\n" + indent)

    ###################################################
    # Helpers
    ###################################################
    def printDetails(self, dest=sys.stdout):
        # get the data
        update_rate = self.getUpdateRate()
        accelUncertaintyDiscrete, accelRandomWalk, accelUncertainty = self.getAccelerometerStatistics()
        gyroUncertaintyDiscrete, gyroRandomWalk, gyroUncertainty = self.getGyroStatistics()

        print >> dest, "  Model: {0}".format(self.data["model"])
        print >> dest, self.extrinsics_field_name
        if self.extrinsics_field_name in self.data:
            print >> dest, self.formatIndented("    ", np.array(self.data[self.extrinsics_field_name]))
        if self.timeshift_field_name in self.data:
            print >> dest, "  time offset with respect to {0}: {1} [s]".format(self.reference_sensor_name, self.data[self.timeshift_field_name])

        print >> dest, "  Update rate: {0}".format(update_rate)
        print >> dest, "  Accelerometer:"
        print >> dest, "    Noise density: {0} ".format(accelUncertainty)
        print >> dest, "    Noise density (discrete): {0} ".format(accelUncertaintyDiscrete)
        print >> dest, "    Random walk: {0}".format(accelRandomWalk)
        print >> dest, "  Gyroscope:"
        print >> dest, "    Noise density: {0}".format(gyroUncertainty)
        print >> dest, "    Noise density (discrete): {0} ".format(gyroUncertaintyDiscrete)
        print >> dest, "    Random walk: {0}".format(gyroRandomWalk)

class LiDARParameters(SensorParametersBase):
    def __init__(self, yamlFile, reference_sensor_name="camera0", createYaml=False):
        SensorParametersBase.__init__(self, yamlFile, "LiDARConfig", reference_sensor_name, createYaml)

    ###################################################
    # Accessors
    ###################################################

    # relative_point_timestamp
    def checkRelativePointTimestamp(self, timestamp):
        if not isinstance(timestamp, bool):
            self.raiseError("relative_point_timestamp has to be a boolean")

    @catch_keyerror
    def getRelativePointTimestamp(self):
        self.checkRelativePointTimestamp(self.data["relative_point_timestamp"])
        return self.data["relative_point_timestamp"]

    def setRelativePointTimestamp(self, timestamp):
        self.checkRelativePointTimestamp(timestamp)
        self.data["relative_point_timestamp"] = timestamp

    # reserved_points_per_frame
    def checkReservedPointsPerFrame(self, num):
        if not isinstance(num, int):
            self.raiseError("reserved_points_per_frame has to be an integer")

    @catch_keyerror
    def getReservedPointsPerFrame(self):
        self.checkReservedPointsPerFrame(self.data["reserved_points_per_frame"])
        return self.data["reserved_points_per_frame"]

    def setRoughlyReservedPointsPerFrame(self, num):
        self.checkReservedPointsPerFrame(num)
        self.data["reserved_points_per_frame"] = num

    ###################################################
    # Helpers
    ###################################################
    def printDetails(self, dest=sys.stdout):
        # get the data
        pass


class ImuSetParameters(ParametersBase):
    def __init__(self, yamlFile, reference_sensor_name, createYaml=False):
        ParametersBase.__init__(self, yamlFile, "ImuSetConfig", createYaml)
        self.imuCount = 0
        self.reference_sensor_name = reference_sensor_name

    def numImus(self):
        return len(self.data)

    def addImuParameters(self, imu_parameters, name=None):
        if name is None:
            name = "imu%d" % self.imuCount
        self.imuCount += 1
        self.data[name] = imu_parameters.getYamlDict()

    @catch_keyerror
    def getImuParameters(self, nr):
        if nr >= self.numImus():
            self.raiseError("out-of-range: IMU index not in IMU set!")

        param = ImuParameters("TEMP_CONFIG", self.reference_sensor_name, createYaml=True)
        param.setYamlDict(self.data['imu{0}'.format(nr)])
        return param

class CalibrationTargetParameters(ParametersBase):
    def __init__(self, yamlFile, createYaml=False):
        ParametersBase.__init__(self, yamlFile, "CalibrationTargetConfig", createYaml)

    ###################################################
    # Accessors
    ###################################################
    def checkTargetType(self, target_type):
        targetTypes = ['aprilgrid',
                       'checkerboard',
                       'circlegrid']

        if target_type not in targetTypes:
            self.raiseError('Unknown calibration target type. Supported types: {0}. )'.format(targetTypes))

    @catch_keyerror
    def getTargetType(self):
        self.checkTargetType(self.data["target_type"])
        return self.data["target_type"]

    @catch_keyerror
    def getTargetParams(self):
        # read target specidic data
        targetType = self.getTargetType()

        if targetType == 'checkerboard':
            try:
                targetRows = self.data["targetRows"]
                targetCols = self.data["targetCols"]
                rowSpacingMeters = self.data["rowSpacingMeters"]
                colSpacingMeters = self.data["colSpacingMeters"]
            except KeyError, e:
                self.raiseError(
                    "Calibration target configuration in {0} is missing the field: {1}".format(self.yamlFile, str(e)))

            if not isinstance(targetRows, int) or targetRows < 3:
                errList.append("invalid targetRows (int>=3)")
            if not isinstance(targetCols, int) or targetCols < 3:
                errList.append("invalid targetCols (int>=3)")
            if not isinstance(rowSpacingMeters, float) or rowSpacingMeters <= 0.0:
                errList.append("invalid rowSpacingMeters (float)")
            if not isinstance(colSpacingMeters, float) or colSpacingMeters <= 0.0:
                errList.append("invalid colSpacingMeters (float)")

            targetParams = {'targetRows': targetRows,
                            'targetCols': targetCols,
                            'rowSpacingMeters': rowSpacingMeters,
                            'colSpacingMeters': colSpacingMeters,
                            'targetType': targetType}

        elif targetType == 'circlegrid':
            try:
                targetRows = self.data["targetRows"]
                targetCols = self.data["targetCols"]
                spacingMeters = self.data["spacingMeters"]
                asymmetricGrid = self.data["asymmetricGrid"]
            except KeyError, e:
                self.raiseError(
                    "Calibration target configuration in {0} is missing the field: {1}".format(self.yamlFile, str(e)))

            if not isinstance(targetRows, int) or targetRows < 3:
                errList.append("invalid targetRows (int>=3)")
            if not isinstance(targetCols, int) or targetCols < 3:
                errList.append("invalid targetCols (int>=3)")
            if not isinstance(spacingMeters, float) or spacingMeters <= 0.0:
                errList.append("invalid spacingMeters (float)")
            if not isinstance(asymmetricGrid, bool):
                errList.append("invalid asymmetricGrid (bool)")

            targetParams = {'targetRows': targetRows,
                            'targetCols': targetCols,
                            'spacingMeters': spacingMeters,
                            'asymmetricGrid': asymmetricGrid,
                            'targetType': targetType}

        elif targetType == 'aprilgrid':
            try:
                numberTargets = self.data["numberTargets"]
                tagRows = self.data["tagRows"]
                tagCols = self.data["tagCols"]
                tagSize = self.data["tagSize"]
                tagSpacing = self.data["tagSpacing"]
            except KeyError, e:
                self.raiseError(
                    "Calibration target configuration in {0} is missing the field: {1}".format(self.yamlFile, str(e)))

            if not isinstance(tagRows, int) or tagRows < 3:
                errList.append("invalid tagRows (int>=3)")
            if not isinstance(tagCols, int) or tagCols < 3:
                errList.append("invalid tagCols (int>=3)")
            if not isinstance(tagSize, float) or tagSize <= 0.0:
                errList.append("invalid tagSize (float)")
            if not isinstance(tagSpacing, float) or tagSpacing <= 0.0:
                errList.append("invalid tagSpacing (float)")

            targetParams = {'numberTargets': numberTargets,
                            'tagRows': tagRows,
                            'tagCols': tagCols,
                            'tagSize': tagSize,
                            'tagSpacing': tagSpacing,
                            'targetType': targetType}

        return targetParams

    ###################################################
    # Helpers
    ###################################################
    def printDetails(self, dest=sys.stdout):

        targetType = self.getTargetType()
        targetParams = self.getTargetParams()

        print >> dest, "  Type: {0}".format(targetType)

        if targetType == 'checkerboard':
            print >> dest, "  Rows"
            print >> dest, "    Count: {0}".format(targetParams['targetRows'])
            print >> dest, "    Distance: {0} [m]".format(targetParams['rowSpacingMeters'])
            print >> dest, "  Cols"
            print >> dest, "    Count: {0}".format(targetParams['targetCols'])
            print >> dest, "    Distance: {0} [m]".format(targetParams['colSpacingMeters'])
        elif targetType == 'aprilgrid':
            print >> dest, "  Tags: "
            print >> dest, "    Rows: {0}".format(targetParams['tagRows'])
            print >> dest, "    Cols: {0}".format(targetParams['tagCols'])
            print >> dest, "    Size: {0} [m]".format(targetParams['tagSize'])
            print >> dest, "    Spacing {0} [m]".format(targetParams['tagSize'] * targetParams['tagSpacing'])


class CameraChainParameters(ParametersBase):
    def __init__(self, yamlFile, reference_sensor_name, createYaml=False):
        ParametersBase.__init__(self, yamlFile, "CameraChainParameters", createYaml)
        self.reference_sensor_name = reference_sensor_name

    ###################################################
    # Accessors
    ###################################################
    def addCameraAtEnd(self, cam):
        if not isinstance(cam, CameraParameters):
            raise RuntimeError("addCamera() requires a CameraParameters object")

        camNr = len(self.data)
        self.data["cam{0}".format(camNr)] = cam.getYamlDict()

    @catch_keyerror
    def getCameraParameters(self, nr):
        if nr >= self.numCameras():
            self.raiseError("out-of-range: camera index not in camera chain!")

        param = CameraParameters("TEMP_CONFIG", self.reference_sensor_name, createYaml=True)
        param.setYamlDict(self.data['cam{0}'.format(nr)])
        return param

    def setExtrinsicsLastCamToHere(self, camNr, extrinsics):
        if camNr == 0:
            raise RuntimeError("setExtrinsicsLastCamToHere(): can't set extrinsics for first cam in chain (cam0=base)")
        if not isinstance(extrinsics, sm.Transformation):
            raise RuntimeError("setExtrinsicsLastCamToHere(): provide extrinsics as an sm.Transformation object")

        self.data["cam{0}".format(camNr)]['T_cn_cnm1'] = extrinsics.T().tolist()

    @catch_keyerror
    def getExtrinsicsLastCamToHere(self, camNr):
        if camNr == 0:
            raise RuntimeError(
                "setExtrinsicsLastCamToHere(): can't get extrinsics for first camera in chain (cam0=base)")

        if camNr >= self.numCameras():
            self.raiseError("out-of-range: baseline index not in camera chain!")

        try:
            trafo = sm.Transformation(np.array(self.data["cam{0}".format(camNr)]['T_cn_cnm1']))
            t = trafo.T()  # for error checking
        except:
            self.raiseError("invalid camera baseline (cam{0} in {1})".format(camNr, self.yamlFile))
        return trafo

    def setExtrinsicsReferenceToCam(self, camNr, extrinsics):
        if not isinstance(extrinsics, sm.Transformation):
            raise RuntimeError("setExtrinsicsReferenceToCam(): provide extrinsics as an sm.Transformation object")
        cam_param = self.getCameraParameters(camNr)
        cam_param.setExtrinsicsReferenceToHere(extrinsics)
        self.data["cam{0}".format(camNr)] = cam_param.getYamlDict()

    @catch_keyerror
    def getExtrinsicsReferenceToCam(self, camNr):
        if camNr >= self.numCameras():
            self.raiseError("out-of-range: cam{0} not in chain!".format(camNr))

        cam_param = self.getCameraParameters(camNr)
        return cam_param.getExtrinsicsReferenceToHere()

    def checkTimeshiftToReference(self, camNr, time_shift):
        if camNr >= self.numCameras():
            self.raiseError("out-of-range: cam{0} not in chain!".format(camNr))

        if not isinstance(time_shift, float):
            self.raiseError("invalid timeshift (cam{0} in {1})".format(camNr, self.yamlFile))

    @catch_keyerror
    def getTimeshiftToReference(self, camNr):
        if camNr >= self.numCameras():
            self.raiseError("out-of-range: cam{0} not in chain!".format(camNr))

        cam_param = self.getCameraParameters(camNr)
        return cam_param.getTimeshiftToReference()

    def setTimeshiftToReference(self, camNr, time_shift):
        self.checkTimeshiftToReference(camNr, time_shift)
        cam_param = self.getCameraParameters(camNr)
        cam_param.setTimeshiftToReference(time_shift)
        self.data["cam{0}".format(camNr)] = cam_param.getYamlDict()

    def checkCamOverlaps(self, camNr, overlap_list):
        if camNr >= self.numCameras():
            self.raiseError("out-of-range: camera id of {0}".format(camNr))

        for cam_id in overlap_list:
            if cam_id >= self.numCameras():
                self.raiseError("out-of-range: camera id of {0}".format(cam_id))

    @catch_keyerror
    def getCamOverlaps(self, camNr):
        self.checkCamOverlaps(camNr, self.data["cam{0}".format(camNr)]["cam_overlaps"])
        return self.data["cam{0}".format(camNr)]["cam_overlaps"]

    def setCamOverlaps(self, camNr, overlap_list):
        self.checkCamOverlaps(camNr, overlap_list)
        self.data["cam{0}".format(camNr)]["cam_overlaps"] = overlap_list

    def numCameras(self):
        return len(self.data)

    def printDetails(self, dest=sys.stdout):
        for camNr in range(0, self.numCameras()):
            print "Camera chain - cam{0}:".format(camNr)
            camConfig = self.getCameraParameters(camNr)
            camConfig.printDetails(dest)

            # print baseline if available
            try:
                T = self.getExtrinsicsLastCamToHere(camNr)
                print >> dest, "  baseline:", T.T()
            except:
                print >> dest, "  baseline: no data available"
                pass
    
    @catch_keyerror
    def getShouldFixLastCamToHere(self, camNr):
        # Checks if extrinsics should be fixed w.r.t. last camera
        # using the 'fix_last_cam_to_here' parameter
        if camNr == 0:
            return False
        if camNr >= self.numCameras():
            self.raiseError("out-of-range: baseline index not in camera chain!")
        
        try:
            return self.data["cam{0}".format(camNr)]['fix_last_cam_to_here']
        except:
            return False
        
    @catch_keyerror
    def getCameraImuOrientationPrior(self, camNr):
        # Obtains a camera-imu orientation prior to help aligning targets between
        # LiDAR and camera in the initialization phase
        if camNr != 0:
            return False
        if camNr >= self.numCameras():
            self.raiseError("out-of-range: baseline index not in camera chain!")
        
        try:
            return self.data["cam{0}".format(camNr)]['camera_imu_orientation_prior']
        except:
            return False


class LiDARListParameters(ParametersBase):
    def __init__(self, yamlFile, reference_sensor_name, createYaml=False):
        ParametersBase.__init__(self, yamlFile, "LiDARListParameters", createYaml)
        self.lidarCount = 0
        self.reference_sensor_name = reference_sensor_name

    def numLiDARs(self):
        return len(self.data)

    @catch_keyerror
    def getLiDARParameters(self, nr):
        if nr >= self.numLiDARs():
            self.raiseError("out-of-range: LiDAR index not in LiDAR list!")

        param = LiDARParameters("TEMP_CONFIG", self.reference_sensor_name, createYaml=True)
        param.setYamlDict(self.data['lidar{0}'.format(nr)])
        return param

    def addLiDARParameters(self, parameters, name=None):
        if name is None:
            name = "lidar%d" % self.lidarCount
        self.lidarCount += 1
        self.data[name] = parameters.getYamlDict()

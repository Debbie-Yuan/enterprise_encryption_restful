import numpy as np


class FaceRecognitionSessionMEM:
    __doc__ = '人脸识别会话 - 阻塞式内存帧模型'

    def __init__(self):
        raise NotImplementedError

    def set_image(self, img: np.ndarry) -> [bool or None, int]:
        """
        控制程序将不断调用set_image函数将接受到的帧(frame, in-memory)在内存中发送给算法，算法需要在10ms可接受下帧内完成处理。
        :param img: 输入的图片
        :return: bool or None :> 是否还需要继续输入图片，如不需要，逻辑将去调用get_result, 这时要求必须返回结果,
                                 若需要前端提示用户进行相应的操作，请为第一个值返回None，第二个返回对应的动作映射值。
        :return: int 动作映射
        """
        raise NotImplementedError

    def get_result(self) -> [bool, int]:
        """

        :return: bool :> 是否识别成功，识别的ID
        """
        raise NotImplementedError

    def __run__(self):
        pass


class FaceRecognitionSessionFile:
    __doc__ = '人脸识别会话 - 阻塞式文件帧模型'

    def __init__(self):
        raise NotImplementedError

    def data_ready_notify(self, temp_prefix):
        """

        :param temp_prefix: 文件的前缀路径（文件夹路径），需要自行删除已经使用的文件，文件名采用timestamp (time.time)

        :return: None
        """
        raise NotImplementedError

    def get_result(self) -> [bool, int]:
        """

        :return: 同 阻塞式内存帧模型
        """
        raise NotImplementedError


class FaceRecognitionSessionAsync:
    __doc__ = '人脸识别会话 - 非阻塞式内存帧模型'

    def __init__(self):
        raise NotImplementedError

    async def set_image(self):
        raise NotImplementedError

    async def get_result(self) -> [bool or None, int]:
        raise NotImplementedError


class FaceRecognitionSessionMT:
    __doc__ = '人脸识别会话 - 多线程内存帧模型'
    # TODO 多线程内存帧模型
    pass


class FaceRecognitionSessionMP:
    __doc__ = '人脸识别会话 - 多进程内存帧模型'
    # TODO 多进程内存帧模型
    pass

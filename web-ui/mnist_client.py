#!/usr/bin/env python2.7
'''
Copyright 2018 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''


from __future__ import print_function

from grpc.beta import implementations
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2


def get_prediction(image, server_host='127.0.0.1', server_port=9000,
                   server_name="server", timeout=10.0):
    """
    Retrieve a prediction from a TensorFlow model server

    :param image:       a MNIST image represented as a 1x784 array
    :param server_host: the address of the TensorFlow server
    :param server_port: the port used by the server
    :param server_name: the name of the server
    :param timeout:     the amount of time to wait for a prediction to complete
    :return 0:          the integer predicted in the MNIST image
    :return 1:          the confidence scores for all classes
    :return 2:          the version number of the model handling the request
    """

    print("connecting to:%s:%i" % (server_host, server_port))
    # initialize to server connection
    channel = implementations.insecure_channel(server_host, server_port)
    stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)

    # build request
    request = predict_pb2.PredictRequest()
    request.model_spec.name = server_name
    request.model_spec.signature_name = 'predict_images'
    request.inputs['images'].CopyFrom(
        tf.contrib.util.make_tensor_proto(image, shape=image.shape))
 
    # retrieve results
    result = stub.Predict(request, timeout)
    resultVal = result.outputs['prediction'].int64_val
    scores = result.outputs['scores'].float_val
    version = result.outputs['model-version'].string_val
    return resultVal[0], scores, version[0]


def random_mnist(save_path=None):
    """
    Pull a random image out of the MNIST test dataset
    Optionally save the selected image as a file to disk

    :param savePath: the path to save the file to. If None, file is not saved
    :return 0: a 1x784 representation of the MNIST image
    :return 1: the ground truth label associated with the image
    :return 2: a bool representing whether the image file was saved to disk
    """

    mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)
    batch_size = 1
    batch_x, batch_y = mnist.test.next_batch(batch_size)
    saved = False
    if save_path is not None:
        # save image file to disk
        try:
            data = (batch_x * 255).astype(np.uint8).reshape(28, 28)
            img = Image.fromarray(data, 'L')
            img.save(save_path)
            saved = True
        except:
            pass
    return batch_x, np.argmax(batch_y), saved

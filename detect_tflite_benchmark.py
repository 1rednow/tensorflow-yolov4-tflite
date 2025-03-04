import core.utils as utils
import tflite_runtime.interpreter as tflite
from absl import app, flags, logging
from absl.flags import FLAGS
#import core.utils as utils
from core.yolov4 import filter_boxes
from PIL import Image
import cv2
import time
import numpy as np

flags.DEFINE_string('framework', 'tf', '(tf, tflite, trt')
flags.DEFINE_string('weights', './checkpoints/yolov4-416',
                    'path to weights file')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_boolean('tiny', False, 'yolo or yolo-tiny')
flags.DEFINE_string('model', 'yolov4', 'yolov3 or yolov4')
flags.DEFINE_string('image', './data/kite.jpg', 'path to input image')
flags.DEFINE_string('output', 'result.png', 'path to output image')
flags.DEFINE_float('iou', 0.45, 'iou threshold')
flags.DEFINE_float('score', 0.25, 'score threshold')

def main(_argv):
    STRIDES, ANCHORS, NUM_CLASS, XYSCALE = utils.load_config(FLAGS)
    input_size = FLAGS.size
    image_path = FLAGS.image

    original_image = cv2.imread(image_path)
    original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

    # image_data = utils.image_preprocess(np.copy(original_image), [input_size, input_size])
    image_data = cv2.resize(original_image, (input_size, input_size))
    image_data = image_data / 255.
    # image_data = image_data[np.newaxis, ...].astype(np.float32)

    images_data = []
    for i in range(1):
        images_data.append(image_data)
    images_data = np.asarray(images_data).astype(np.float32)

    if FLAGS.framework == 'tflite':
        interpreter = tflite.Interpreter(model_path=FLAGS.weights)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        print(input_details)
        print(output_details)
        interpreter.set_tensor(input_details[0]['index'], images_data)
        interpreter.invoke()
        pred = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
        #if FLAGS.model == 'yolov3' and FLAGS.tiny == True:
        #    boxes, pred_conf = filter_boxes(pred[1], pred[0], score_threshold=0.25, input_shape=tf.constant([input_size, input_size]))
        #else:
        #    boxes, pred_conf = filter_boxes(pred[0], pred[1], score_threshold=0.25, input_shape=tf.constant([input_size, input_size]))

    #boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
    #    boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
    #    scores=tf.reshape(
    #        pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
    #    max_output_size_per_class=50,
    #    max_total_size=50,
    #    iou_threshold=FLAGS.iou,
    #    score_threshold=FLAGS.score
    #)
    #pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
    #image = utils.draw_bbox(original_image, pred_bbox)
    ## image = utils.draw_bbox(image_data*255, pred_bbox)
    #image = Image.fromarray(image.astype(np.uint8))
    ##image.show()
    #image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    #cv2.imwrite(FLAGS.output, image)
    sum = 0
    for i in range(1000):
        prev_time = time.time()
        if FLAGS.framework == 'tflite':
            interpreter.set_tensor(input_details[0]['index'], images_data)
            interpreter.invoke()
            pred = [interpreter.get_tensor(output_details[i]['index']) for i in range(len(output_details))]
        curr_time = time.time()
        exec_time = curr_time - prev_time
        if i == 0: continue
        sum += (1 / exec_time)
        info = str(i) + " time:" + str(round(exec_time, 3)) + " average FPS:" + str(round(sum / i, 2)) + ", FPS: " + str(
            round((1 / exec_time), 1))
        print(info)

if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass

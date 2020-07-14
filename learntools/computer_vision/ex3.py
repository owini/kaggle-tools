from learntools.core import *
import tensorflow as tf

class Q1(CodingProblem):
    _vars = ['image_condense']
    _hint = """
You'll need `window_shape=2` and `pooling_type='MAX'`.
"""
    _solution = CS("""
image_condense = tf.nn.pool(
    input=image_detect,
    window_shape=2, # or (2, 2)
    pooling_type='MAX',
    strides=2, # or (2, 2)
    padding='SAME',
)
""")

    def check(self, image_condense):
        size = [99, 99]
        image_size = tf.squeeze(image_condense).shape.as_list()
        assert image_size == size, \
            (("The size of `image_condense` should be `{}`, but actually is `{}`." +
              "Did you use `padding='SAME'` and `strides=2`?")
             .format(size, image_size))

        
class Q2(ThoughtExperiment):
    _hint = "If you only had the final output to look at, would you be able to pick which circle originally produced it?"
    _solution ="""It would not be helpful. This exercise illustrates how maximum pooling creates the *translation invariance over small distances* we discussed in the tutorial. The maximum pooling operations reduce each of the inputs to an identical output. There wouldn't be any extra information being passed on to the head for classification.

Note, however, that this invariance only applies over *small* distances. Translating the circle by a larger amount actually could improve the classification. In fact, this method of transforming an image in random ways whenever it's used in training is known as **data augmentation**. Data augmentation is a common way of improving a classifier. You'll learn how to use it in Keras in Lesson 6.
"""


# Free
class Q3A(CodingProblem):
    _hint = ""
    _solution = ""
    def check(self):
        pass
    
class Q3B(ThoughtExperiment):
    _hint = """VGG16 creates 512 features maps from an image, which might represent something like a wheel or a window. Each square in *Pooled Feature Maps* represents a feature. What would a large value for a feature mean?"""
    _solution = """The VGG16 base produces 512 feature maps. We can think of each feature map as representing some high-level visual feature in the original image -- maybe a wheel or window. Pooling a map gives us a single number, which we could think of as a *score* for that feature: large if the feature is present, small if it is absent. Cars tend to score high with one set of features, and Trucks score high with another. Now, instead of trying to map raw features to classes, the head only has to work with these scores that `GlobalAvgPool2D` produced, a much easier problem for it to solve.
"""

Q3 = MultipartProblem(Q3A, Q3B)


qvars = bind_exercises(globals(), [
        Q1, Q2, Q3,
    ],
    var_format='q_{n}',
)
__all__ = list(qvars)

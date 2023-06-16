from keras.callbacks import ModelCheckpoint, TensorBoard
from keras.layers import BatchNormalization, Lambda, Input, Dense, Convolution2D, MaxPooling2D, Dropout, Flatten
from keras.layers.merging import Concatenate
from keras.models import Model
from keras.optimizers import SGD
from keras.preprocessing.image import ImageDataGenerator


def create_top_conv(input_layer):
    top_conv = Convolution2D(filters=48, kernel_size=(11, 11), strides=(4, 4), activation='relu')(input_layer)
    top_conv = BatchNormalization()(top_conv)
    top_conv = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(top_conv)
    return top_conv


def create_bottom_conv(input_layer):
    bottom_conv = Convolution2D(filters=48, kernel_size=(11, 11), strides=(4, 4), activation='relu')(input_layer)
    bottom_conv = BatchNormalization()(bottom_conv)
    bottom_conv = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(bottom_conv)
    return bottom_conv


def color_net(num_classes):
    # placeholder for input image
    input_image = Input(shape=(224, 224, 3))

    # ============================================= TOP BRANCH ===================================================
    # first top convolution layer
    top_conv1 = create_top_conv(input_image)

    # second top convolution layer
    # split feature map by half
    top_top_conv2 = Lambda(lambda x: x[:, :, :, :24])(top_conv1)
    top_bot_conv2 = Lambda(lambda x: x[:, :, :, 24:])(top_conv1)

    top_top_conv2 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_top_conv2)
    top_top_conv2 = BatchNormalization()(top_top_conv2)
    top_top_conv2 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(top_top_conv2)

    top_bot_conv2 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_bot_conv2)
    top_bot_conv2 = BatchNormalization()(top_bot_conv2)
    top_bot_conv2 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(top_bot_conv2)

    # third top convolution layer
    # concat 2 feature maps
    top_conv3 = Concatenate()([top_top_conv2, top_bot_conv2])
    top_conv3 = Convolution2D(filters=192, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_conv3)

    # fourth top convolution layer
    # split feature map by half
    top_top_conv4 = Lambda(lambda x: x[:, :, :, :96])(top_conv3)
    top_bot_conv4 = Lambda(lambda x: x[:, :, :, 96:])(top_conv3)

    top_top_conv4 = Convolution2D(filters=96, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_top_conv4)
    top_bot_conv4 = Convolution2D(filters=96, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_bot_conv4)

    # fifth top convolution layer
    top_top_conv5 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_top_conv4)
    top_top_conv5 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(top_top_conv5)

    top_bot_conv5 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_bot_conv4)
    top_bot_conv5 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(top_bot_conv5)

    # ============================================= BOTTOM BRANCH ===================================================
    # first bottom convolution layer
    bottom_conv1 = create_bottom_conv(input_image)

    # second bottom convolution layer
    # split feature map by half
    bottom_top_conv2 = Lambda(lambda x: x[:, :, :, :24])(bottom_conv1)
    bottom_bot_conv2 = Lambda(lambda x: x[:, :, :, 24:])(bottom_conv1)

    bottom_top_conv2 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_top_conv2)
    bottom_top_conv2 = BatchNormalization()(bottom_top_conv2)
    bottom_top_conv2 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(bottom_top_conv2)

    bottom_bot_conv2 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_bot_conv2)
    bottom_bot_conv2 = BatchNormalization()(bottom_bot_conv2)
    bottom_bot_conv2 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(bottom_bot_conv2)

    # third bottom convolution layer
    # concat 2 feature maps
    bottom_conv3 = Concatenate()([bottom_top_conv2, bottom_bot_conv2])
    bottom_conv3 = Convolution2D(filters=192, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_conv3)

    # fourth bottom convolution layer
    # split feature map by half
    bottom_top_conv4 = Lambda(lambda x: x[:, :, :, :96])(bottom_conv3)
    bottom_bot_conv4 = Lambda(lambda x: x[:, :, :, 96:])(bottom_conv3)

    bottom_top_conv4 = Convolution2D(filters=96, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_top_conv4)
    bottom_bot_conv4 = Convolution2D(filters=96, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_bot_conv4)

    # fifth bottom convolution layer
    bottom_top_conv5 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_top_conv4)
    bottom_top_conv5 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(bottom_top_conv5)

    bottom_bot_conv5 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_bot_conv4)
    bottom_bot_conv5 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(bottom_bot_conv5)

    # ======================================== CONCATENATE TOP AND BOTTOM BRANCH =================================
    conv_output = Concatenate()([top_top_conv5, top_bot_conv5, bottom_top_conv5, bottom_bot_conv5])

    # Flatten
    flatten = Flatten()(conv_output)

    # Fully-connected layer
    FC_1 = Dense(units=4096, activation='relu')(flatten)
    FC_1 = Dropout(0.6)(FC_1)
    FC_2 = Dense(units=4096, activation='relu')(FC_1)
    FC_2 = Dropout(0.6)(FC_2)
    output = Dense(units=num_classes, activation='softmax')(FC_2)

    model = Model(inputs=input_image, outputs=output)
    sgd = SGD(lr=1e-3, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(optimizer=sgd, loss='categorical_crossentropy', metrics=['accuracy'])

    return model


img_rows, img_cols = 224, 224
num_classes = 15
batch_size = 32
nb_epoch = 5

# initialise model
model = color_net(num_classes)

filepath = 'color_weights_test.hdf5'
checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
tensorboard = TensorBoard(log_dir='./logs', histogram_freq=0, batch_size=32, write_graph=True, write_grads=False,
                          write_images=False, embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None,
                          embeddings_data=None, update_freq='batch')
callbacks_list = [checkpoint, tensorboard]

train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.3,
    horizontal_flip=True,
    dtype='float32')

test_datagen = ImageDataGenerator(rescale=1. / 255, dtype='float32')

training_set = train_datagen.flow_from_directory(
    'dataset/train/',
    target_size=(img_rows, img_cols),
    batch_size=batch_size,
    class_mode='categorical')

test_set = test_datagen.flow_from_directory(
    'dataset/test/',
    target_size=(img_rows, img_cols),
    batch_size=batch_size,
    class_mode='categorical')

label_map = (test_set.class_indices)

model.fit_generator(
    training_set,
    steps_per_epoch=2892,
    epochs=nb_epoch,
    validation_data=test_set,
    validation_steps=665,
    callbacks=callbacks_list)

model.save('color_model.h5')


def create_top_conv(input_layer):
    top_conv = Convolution2D(filters=48, kernel_size=(11, 11), strides=(4, 4), activation='relu')(input_layer)
    top_conv = BatchNormalization()(top_conv)
    top_conv = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(top_conv)
    return top_conv


def create_bottom_conv(input_layer):
    bottom_conv = Convolution2D(filters=48, kernel_size=(11, 11), strides=(4, 4), activation='relu')(input_layer)
    bottom_conv = BatchNormalization()(bottom_conv)
    bottom_conv = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(bottom_conv)
    return bottom_conv


def color_net(num_classes):
    # placeholder for input image
    input_image = Input(shape=(224, 224, 3))

    # ============================================= TOP BRANCH ===================================================
    # first top convolution layer
    top_conv1 = create_top_conv(input_image)

    # second top convolution layer
    # split feature map by half
    top_top_conv2 = Lambda(lambda x: x[:, :, :, :24])(top_conv1)
    top_bot_conv2 = Lambda(lambda x: x[:, :, :, 24:])(top_conv1)

    top_top_conv2 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_top_conv2)
    top_top_conv2 = BatchNormalization()(top_top_conv2)
    top_top_conv2 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(top_top_conv2)

    top_bot_conv2 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_bot_conv2)
    top_bot_conv2 = BatchNormalization()(top_bot_conv2)
    top_bot_conv2 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(top_bot_conv2)

    # third top convolution layer
    # concat 2 feature maps
    top_conv3 = Concatenate()([top_top_conv2, top_bot_conv2])
    top_conv3 = Convolution2D(filters=192, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_conv3)

    # fourth top convolution layer
    # split feature map by half
    top_top_conv4 = Lambda(lambda x: x[:, :, :, :96])(top_conv3)
    top_bot_conv4 = Lambda(lambda x: x[:, :, :, 96:])(top_conv3)

    top_top_conv4 = Convolution2D(filters=96, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_top_conv4)
    top_bot_conv4 = Convolution2D(filters=96, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_bot_conv4)

    # fifth top convolution layer
    top_top_conv5 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_top_conv4)
    top_top_conv5 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(top_top_conv5)

    top_bot_conv5 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        top_bot_conv4)
    top_bot_conv5 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(top_bot_conv5)

    # ============================================= BOTTOM BRANCH ===================================================
    # first bottom convolution layer
    bottom_conv1 = create_bottom_conv(input_image)

    # second bottom convolution layer
    # split feature map by half
    bottom_top_conv2 = Lambda(lambda x: x[:, :, :, :24])(bottom_conv1)
    bottom_bot_conv2 = Lambda(lambda x: x[:, :, :, 24:])(bottom_conv1)

    bottom_top_conv2 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_top_conv2)
    bottom_top_conv2 = BatchNormalization()(bottom_top_conv2)
    bottom_top_conv2 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(bottom_top_conv2)

    bottom_bot_conv2 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_bot_conv2)
    bottom_bot_conv2 = BatchNormalization()(bottom_bot_conv2)
    bottom_bot_conv2 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(bottom_bot_conv2)

    # third bottom convolution layer
    # concat 2 feature maps
    bottom_conv3 = Concatenate()([bottom_top_conv2, bottom_bot_conv2])
    bottom_conv3 = Convolution2D(filters=192, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_conv3)

    # fourth bottom convolution layer
    # split feature map by half
    bottom_top_conv4 = Lambda(lambda x: x[:, :, :, :96])(bottom_conv3)
    bottom_bot_conv4 = Lambda(lambda x: x[:, :, :, 96:])(bottom_conv3)

    bottom_top_conv4 = Convolution2D(filters=96, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_top_conv4)
    bottom_bot_conv4 = Convolution2D(filters=96, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_bot_conv4)

    # fifth bottom convolution layer
    bottom_top_conv5 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_top_conv4)
    bottom_top_conv5 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(bottom_top_conv5)

    bottom_bot_conv5 = Convolution2D(filters=64, kernel_size=(3, 3), strides=(1, 1), activation='relu', padding='same')(
        bottom_bot_conv4)
    bottom_bot_conv5 = MaxPooling2D(pool_size=(3, 3), strides=(2, 2))(bottom_bot_conv5)

    # ======================================== CONCATENATE TOP AND BOTTOM BRANCH =================================
    conv_output = Concatenate()([top_top_conv5, top_bot_conv5, bottom_top_conv5, bottom_bot_conv5])

    # Flatten
    flatten = Flatten()(conv_output)

    # Fully-connected layer
    FC_1 = Dense(units=4096, activation='relu')(flatten)
    FC_1 = Dropout(0.6)(FC_1)
    FC_2 = Dense(units=4096, activation='relu')(FC_1)
    FC_2 = Dropout(0.6)(FC_2)
    output = Dense(units=num_classes, activation='softmax')(FC_2)

    model = Model(inputs=input_image, outputs=output)
    sgd = SGD(lr=1e-3, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(optimizer=sgd, loss='categorical_crossentropy', metrics=['accuracy'])

    return model


img_rows, img_cols = 224, 224
num_classes = 15
batch_size = 32
nb_epoch = 5

# initialise model
model = color_net(num_classes)

filepath = 'color_weights_test.hdf5'
checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max')
tensorboard = TensorBoard(log_dir='./logs', histogram_freq=0, batch_size=32, write_graph=True, write_grads=False,
                          write_images=False, embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None,
                          embeddings_data=None, update_freq='batch')
callbacks_list = [checkpoint, tensorboard]

train_datagen = ImageDataGenerator(
    rescale=1. / 255,
    shear_range=0.2,
    zoom_range=0.3,
    horizontal_flip=True,
    dtype='float32')

test_datagen = ImageDataGenerator(rescale=1. / 255, dtype='float32')

training_set = train_datagen.flow_from_directory(
    'dataset/train/',
    target_size=(img_rows, img_cols),
    batch_size=batch_size,
    class_mode='categorical')

test_set = test_datagen.flow_from_directory(
    'dataset/test/',
    target_size=(img_rows, img_cols),
    batch_size=batch_size,
    class_mode='categorical')

label_map = (test_set.class_indices)

model.fit_generator(
    training_set,
    steps_per_epoch=2892,
    epochs=nb_epoch,
    validation_data=test_set,
    validation_steps=665,
    callbacks=callbacks_list)

model.save('color_model.h5')

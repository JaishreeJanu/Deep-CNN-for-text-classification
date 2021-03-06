# based on ideas from https://github.com/dennybritz/cnn-text-classification-tf

import numpy as np
import json

alphabet = "abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:'\"/\\|_@#$%^&*~`+-=<>()[]{}\n"
char_seq_length = 144 # Twitter has only 140 characters. We pad 4 blanks characters more to the right of tweets to be conformed with the architecture of A. Conneau et al (2016)


def load_yelp(alphabet):
    examples = []
    labels = []
    with open('./yelp-review-dataset/yelp_academic_dataset_review.json') as f:
        i = 0
        for line in f:
            review = json.loads(line)
            stars = review["stars"]
            text = review["text"]
            if stars != 3:
                padded = pad_sentence(list(text.lower()))
                text_float32_repr = string_to_float32_conversion(padded, alphabet)
                if stars == 1 or stars == 2:
                    labels.append([1, 0])
                    examples.append(text_float32_repr)
                elif stars == 4 or stars == 5:
                    labels.append([0, 1])
                    examples.append(text_float32_repr)
                i += 1
                if i % 100000 == 0:
                    print("Non-neutral instances processed: " + str(i))
            if i == 200000:                                                           ## Added extra
                break
                
    return examples, labels

def pad_sentence(char_seq, padding_char=" "):
    num_padding = char_seq_length - len(char_seq)
    new_char_seq = char_seq + [padding_char] * num_padding
    return new_char_seq


def string_to_float32_conversion(char_seq, alphabet):
    x = np.array([alphabet.find(char) for char in char_seq], dtype=np.float32)
    return x


def get_batched_one_hot(char_seqs_indices, labels, start_index, end_index):
    x_batch = char_seqs_indices[start_index:end_index]
    y_batch = labels[start_index:end_index]
    x_batch_one_hot = np.zeros(shape=[len(x_batch), len(alphabet), len(x_batch[0]), 1])
    for example_i, char_seq_indices in enumerate(x_batch):
        for char_pos_in_seq, char_seq_char_ind in enumerate(char_seq_indices):
            if char_seq_char_ind != -1:
                x_batch_one_hot[example_i][char_seq_char_ind][char_pos_in_seq][0] = 1
    return [x_batch_one_hot, y_batch]


def load_data():
    examples, labels = load_yelp(alphabet)
    x = np.array(examples, dtype=object)     ## changed from np.float32
    y = np.array(labels, dtype=object)
    print("x_char_seq_ind=" + str(x.shape))
    print("y shape=" + str(y.shape))
    return [x, y]


def batch_iter(x, y, batch_size, num_epochs, shuffle=True):
    """
    Generates a batch iterator for a dataset.
    """
    # data = np.array(data)
    data_size = len(x)
    num_batches_per_epoch = int(data_size/batch_size) + 1
    for epoch in range(num_epochs):
        print("In epoch >> " + str(epoch + 1))
        print("num batches per epoch is: " + str(num_batches_per_epoch))
        # Shuffle the data at each epoch
        if shuffle:
            shuffle_indices = np.random.permutation(np.arange(data_size))
            x_shuffled = x[shuffle_indices]
            y_shuffled = y[shuffle_indices]
        else:
            x_shuffled = x
            y_shuffled = y
        for batch_num in range(num_batches_per_epoch):
            start_index = batch_num * batch_size
            end_index = min((batch_num + 1) * batch_size, data_size)
            x_batch, y_batch = get_batched_one_hot(x_shuffled, y_shuffled, start_index, end_index)
            batch = list(zip(x_batch, y_batch))
            yield batch

#!/usr/bin/env python3

import math
import pandas as pd
import tensorflow as tf

import idseq_dag.util.command as command
import idseq_dag.util.data_wrangling as dw

def main():
    # Prepare data
    warehouse_dir = "/mnt/idseq/warehouse"
    model_dir = f"{warehouse_dir}/models"
    command.execute(f"mkdir -p {model_dir}")
    idseq_coverages = f"{warehouse_dir}/coverage_histograms.csv"
    cami_labels = f"{warehouse_dir}/cami_labels.csv"
    
    feature_df = dw.subset(pd.read_csv(idseq_coverages, index_col=[0]),
                           tax_level=2)
    label_df = dw.subset(pd.read_csv(cami_labels, index_col=[0]),
                         tax_level=2)
    df = pd.merge(feature_df, label_df, how='outer', on=['taxid', 'tax_level', 'sample_name'], suffixes=('', ''))
    df = df.fillna(0)

    holdout_sample = "2017-12-04_18-56-22_sample_23"
    train_df = df.loc[df['sample_name'] != "2017-12-04_18-56-22_sample_23"]
    test_df = df.loc[df['sample_name'] == "2017-12-04_18-56-22_sample_23"]

    Y_train = train_df[['count']]
    Y_test = test_df[['count']]
    coverage_values = [col for col in df.columns if dw.can_convert_to_int(col)]
    X_train = train_df.reindex(columns = coverage_values)
    X_test = test_df.reindex(columns = coverage_values)

    # Build model
    learning_rate = 0.1
    batch_size = 100
    num_steps = math.ceil(X_train.shape[0] / batch_size)
    display_step = 10

    n_hidden1 = 50
    num_input = len(X_train.columns)
    num_output = 1

    X = tf.placeholder("float", [None, num_input])
    Y = tf.placeholder("float", [None, num_output])

    weights = {
        'h1': tf.Variable(tf.random_normal([num_input, n_hidden1])),
        'out': tf.Variable(tf.random_normal([n_hidden1, num_output]))
    }
    biases = {
        'b1': tf.Variable(tf.random_normal([n_hidden1])),
        'out': tf.Variable(tf.random_normal([num_output]))
    }

    def neural_net(x):
        layer1 = tf.add(tf.matmul(x, weights['h1']), biases['b1'])
        out_layer = tf.matmul(layer1, weights['out']) + biases['out']
        return out_layer

    Y_pred = neural_net(X)
    loss_op = tf.reduce_mean(tf.losses.mean_squared_error(Y, Y_pred))
    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train_op = optimizer.minimize(loss_op)

    init = tf.global_variables_initializer()

    # Train and evaluate
    with tf.Session() as sess:
        sess.run(init)

        for step in range(0, num_steps):
            batch_start = step*batch_size
            batch_end = batch_start + batch_size - 1
            batch_x = X_train.iloc[batch_start:batch_end]
            batch_y = Y_train.iloc[batch_start:batch_end]
            sess.run(train_op, feed_dict={X: batch_x, Y: batch_y})
            if step % display_step == 0:
                loss = sess.run(loss_op, feed_dict={X: batch_x, Y: batch_y})
                print(f"Step {step}, Minibatch Loss = {loss:.4f}")

        print("Optimization Finished!")

        test_MSE = sess.run(loss_op, feed_dict={X: X_test, Y: Y_test})
        print(f"Test RMSE = {math.sqrt(test_MSE)}")

if __name__ == "__main__":
    main()

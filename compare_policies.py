import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
import onnx
import onnxruntime as ort
from collections import defaultdict
np.set_printoptions(threshold=10_000)

OBS_SIZE = 61
ACT_SIZE = 6
DIV_SIZE = 4


def load_and_plot():
    envs = [
        #{"env_name" : "WormDiverse", "gmm_run_id" : "gmm-worm1fix3", "mede_run_id": "mede-worm-outprior"}
        {"env_name" : "BasicDiverse", "gmm_run_id" : "gmm-q-exp", "mede_run_id": "mede-q-exp"}
            ]  

    for env in envs:
        env_name = env["env_name"]
#        x = np.zeros((1,OBS_SIZE), dtype=np.float32)

        gmm_run_id = env["gmm_run_id"]
        #gmm_model_path = "results/" + gmm_run_id + "/" + env_name + ".onnx"
        #gmm_ort_sess = ort.InferenceSession(gmm_model_path)
        #gmm_outputs = gmm_ort_sess.run(None, {'obs_0': x}) 
        #for out in gmm_outputs:
        #    print(out)

        mede_run_id = env["mede_run_id"]
        mede_model_path = "results/" + mede_run_id + "/" + env_name + ".onnx"
        prior_model_path = "results/" + mede_run_id + "/" + env_name + "_Prior.onnx"
        mede_q_model_path = "results/" + mede_run_id + "/" + env_name + "_Q.onnx"
        sac_q_model_path = "results/" + gmm_run_id + "/" + env_name + "_sac_Q.onnx"

        states = [[0,0],[0,1],[1,1]]
        #states = [[0,0]]
#        x = np.array([[0,0]], dtype=np.float32)
        fig, axs = plt.subplots(DIV_SIZE + 2, len(states))
        prior_ort_sess = ort.InferenceSession(prior_model_path)
        mede_ort_sess = ort.InferenceSession(mede_model_path)
        mede_q_ort_sess = ort.InferenceSession(mede_q_model_path)
        sac_q_ort_sess = ort.InferenceSession(sac_q_model_path)
        X, Y = np.mgrid[-1:1:21j, -1:1:21j]
        actions = (np.vstack((-1 * X.flatten(), Y.flatten())).T).astype(np.float32)

        mems = np.zeros((1, 1, 0), dtype=np.float32)
        state_to_div_val = defaultdict(list)
        for i, state in enumerate(states):
            x = np.array([state], dtype=np.float32)
            prior_outputs = prior_ort_sess.run(None, {'obs_1': x}) 
            x_q = np.repeat(x, len(actions), axis=0)
            sac_q_outputs = sac_q_ort_sess.run(None, {'obs_0': x_q, 'continuous_action': actions, '2': mems}) 
            sac_q = np.reshape(sac_q_outputs[0], (441, len(x))).T
            vals = np.reshape(sac_q, (21, 21))
            if len(states) > 1:
                axs[0, i].imshow(vals)
            else:
                axs[0].imshow(vals)

            for div in range(DIV_SIZE):
                div_oh = np.zeros((len(x), DIV_SIZE), dtype=np.float32)
                div_oh[:, div] = 1
                mede_outputs = mede_ort_sess.run(None, {'obs_0': div_oh, 'obs_1': x}) 
                #print(mede_outputs)
                div_oh_q = np.repeat(div_oh, len(actions), axis=0)
                #print(onnx.load(mede_q_model_path))
                mede_q = mede_q_ort_sess.run(None, {'obs_0': div_oh_q, 'obs_1': x_q, 'continuous_action': actions, '3': mems})
                mede_q = np.reshape(mede_q[0], (441, len(x))).T
                for vals in mede_q:
                    vals = np.reshape(vals, (21,21))
                    state_to_div_val[i].append(vals)
                    if len(states) > 1:
                        axs[div+1, i].imshow(vals)
                    else:
                        axs[div+1].imshow(vals)
            #aggr = np.sum(state_to_div_val[i], axis=0)
            #aggr = 0
            #for prior, val in zip(prior_outputs[0][0], state_to_div_val[i]):
            #    aggr +=  np.log(prior * np.exp(val))
            #if len(states) > 1:
            #    axs[DIV_SIZE + 1, i].imshow(aggr)
            #else:
            #    axs[DIV_SIZE + 1].imshow(aggr)

        plt.savefig(env_name + ".png")
        plt.close()



if __name__ == "__main__":
    load_and_plot()






x = np.array([[ 5.3230e-02,  0.0000e+00,  0.0000e+00,  1.0000e+00,  4.7738e-01,
          8.7804e-02,  5.2101e-01, -4.9973e-02,  8.4755e-01, -4.3201e-03,
         -3.2188e-02,  1.1182e+01,  1.0000e+00, -9.0608e-02,  1.7623e-01,
          5.8515e+00,  1.0246e+01, -2.0843e+00, -4.5309e+00,  1.0000e+00,
          2.0615e-01, -3.8244e-02,  4.8343e+00,  1.2312e+01,  1.3794e+00,
          1.5440e+00,  1.2056e+00, -1.7177e-01, -2.4889e-01,  4.7423e-01,
         -1.5757e-01,  8.4867e-02,  8.6202e-01,  1.0000e+00,  9.4751e-01,
         -1.5074e+00,  3.2044e+00,  1.0436e+01,  3.0039e+00,  6.0190e+00,
          2.2112e+00, -1.3960e-01,  1.9047e-01, -1.4100e-01, -2.9674e-02,
          1.8479e-01,  9.7216e-01,  1.0000e+00, -3.4296e+00, -6.8809e-01,
          5.1132e+00,  6.3698e+00, -1.6245e+00,  1.3983e+01,  2.8777e+00,
          2.5864e-01,  9.1920e-01, -4.6224e-02, -1.6730e-02,  3.0680e-01,
          9.5050e-01],
        [ 4.7545e-02,  2.9802e-08,  0.0000e+00,  1.0000e+00,  4.4395e-01,
         -7.1605e-02,  5.3461e-01, -2.8262e-02,  8.4159e-01,  5.2292e-03,
          2.3707e-02,  8.9228e+00,  1.0000e+00, -5.4978e-01, -9.5281e-02,
          5.8993e+00,  1.1097e+01, -7.5119e-01, -4.4707e+00,  1.0000e+00,
         -7.4145e-01,  2.0742e-01,  5.9935e+00,  1.2086e+01, -6.4592e-01,
         -8.9633e-01,  1.2344e+00, -6.9752e-02, -3.5599e-01,  8.3270e-01,
         -4.3044e-02,  6.6549e-02,  5.4802e-01,  1.0000e+00,  1.7525e-01,
         -1.0657e+00,  6.3644e+00,  9.3401e+00,  4.2773e+00,  6.5823e+00,
          2.1829e+00,  8.1444e-02,  1.6770e-02,  2.9745e-01,  9.2181e-02,
          2.6917e-01,  9.1136e-01,  0.0000e+00,  6.4774e-01,  1.6878e+00,
          5.4992e+00,  8.8089e+00,  1.9478e+00,  1.0185e+01,  3.0958e+00,
          3.1049e-01,  5.6414e-01, -1.1620e-01,  2.3045e-02, -1.9309e-01,
          9.7400e-01],
        [ 3.9171e-02, -1.4901e-08,  0.0000e+00,  1.0000e+00,  7.3676e-01,
         -1.0929e-02, -5.9361e-01, -2.5469e-03,  8.0467e-01, -1.0691e-02,
          1.1628e-01,  5.2736e+01,  1.0000e+00,  7.6441e-01,  8.5823e-01,
          3.5943e+00,  1.3868e+01, -1.0830e+00,  4.9227e+00,  1.0000e+00,
          1.3200e+00,  9.7010e-02,  3.6533e+00,  1.0009e+01,  2.3920e+00,
         -5.9332e+00, -1.1968e+00, -2.8464e-02,  4.5090e-02,  4.1392e-01,
         -2.7720e-01,  1.3252e-01,  8.5689e-01,  1.0000e+00,  3.5103e-01,
          1.3307e+00,  3.6643e+00,  8.1989e-01, -7.0239e+00, -1.6090e+01,
         -1.7856e+00,  9.2624e-02,  8.8010e-01, -3.8243e-01, -6.7933e-02,
          1.4327e-01,  9.1028e-01,  0.0000e+00, -1.1528e+00,  4.7461e-01,
          3.7393e+00,  7.1241e+00, -5.6125e+00, -1.5205e+01, -2.0184e+00,
          4.0534e-01,  1.9287e+00, -9.0143e-04, -1.3439e-04,  1.5742e-02,
          9.9988e-01],
        [ 4.9099e-02,  0.0000e+00,  0.0000e+00,  1.0000e+00,  4.6146e-01,
         -1.1455e-01, -5.5303e-01, -2.6504e-02,  8.2482e-01, -2.3460e-03,
          7.0301e-03,  3.8356e+01,  1.0000e+00,  6.0878e-02, -1.4794e-01,
          6.3782e+00,  8.7085e+00,  3.0025e+00,  3.3418e+00,  1.0000e+00,
         -1.0605e+00,  8.4291e-02,  4.8758e+00,  7.6932e+00, -4.6651e+00,
         -2.5904e+00, -1.2314e+00, -1.5455e-01, -1.6003e-01,  5.2480e-01,
          2.1586e-01, -1.3752e-01,  8.1183e-01,  1.0000e+00, -2.0235e+00,
         -2.0364e+00,  3.5638e+00,  8.9821e+00, -2.2644e+00, -3.0043e+00,
         -2.1480e+00,  3.7272e-02,  3.6155e-01, -9.0736e-02,  2.8028e-02,
         -2.9205e-01,  9.5168e-01,  0.0000e+00, -4.4067e-01, -1.1017e+00,
          6.9123e+00,  5.7646e+00,  3.7673e+00, -9.4744e+00, -2.9784e+00,
          3.3722e-01,  1.0374e+00,  1.7727e-02,  1.7632e-03,  1.1506e-01,
          9.9320e-01]], dtype=np.float32)


<h2 align = "center">
DroneMOT: Drone-based Multi-Object Tracking Considering Detection Difficulties and Simultaneous Moving of Drones and Objects
</h2>
<h4 align = "center" >
Proceedings of <a href="https://2024.ieee-icra.org/">ICRA 2024</a>
</h4>


Peng Wang^1^, Yongcai Wang^1,*^, Deying Li^1^

^1^ School of Information, Renmin University of China, Beijing, 100872 



<center>
  <a href="DroneMOT.pdf"><img height= "50" src="https://p.ipic.vip/f50s58.png" alt="image-20240529183359317"  /> 
  </a>
  <a href="https://github.com/PenK1nG/DroneMOT">
  <img height= "50" src="https://p.ipic.vip/exxqen.png" alt="image-20240529183422179"/>
  </a>  
</center>




<video controls="controls" autoplay="autoplay" src="DroneMOT.mp4" type="video/mp4"></video>


<h2 align = "center">
Overview 
</h2>
This paper proposes DroneMOT, which firstly proposes a Dual-domain Integrated Attention (DIA) module that considers the fast movements of drones to enhance the drone-based object detection and feature embedding for smallsized, blurred, and occluded objects. Then, an innovative Motion-Driven Association (MDA) scheme is introduced, considering the concurrent movements of both the drone and the objects. Within MDA, an Adaptive Feature Synchronization (AFS) technique is presented to update the object features seen from different angles. Additionally, a Dual Motion-based Prediction (DMP) method is employed to forecast the object positions. Finally, both the refined feature embeddings and the predicted positions are integrated to enhance the object association. Comprehensive evaluations on VisDrone2019-MOT and UAVDT datasets show that DroneMOT provides substantial performance improvements over the state-of-the-art in the domain of MOT on drones.

<h2 align = "center">
System Architecture 
</h2>
DroneMOT is primarily split into two modules: **the network module** for detection and feature embedding, and **the data-association module** based on the result of the network module. The image $I_t ∈ R^{W ×H×3}$  captured by the moving drone at the $t-th$ frame is fed into the network along with the previous frame image $I_{t−1}$ . The results of the network module, represented by $O_t = \{ o_1 , o_2 , · · · , o_i , · · · , o_M \}$ consist of M detections where $o_i = (b_i , s_i , f_i )$. Here, $b_i$ represents the bounding box $(x, y, w, h)$, $s_i$ is the detection score, and $f_i$ is the feature embedding vectors. The data association module takes the detections $O_t$ and all $N$ stored trajectories of the objects $T_{t−1} = \{ T_1 , T_2 , · · · , T_j , · · · , T_N \}$ as inputs, where $T_j = \{ o_{j_1} , o_{j_3} , · · · , o_{j_{t−1}} \}$ , and $o_{j_{t−1}}$represents the detection associated with the trajectory $j$ in the $t−1-th$ frame. The goal of the data association module is to match each detection with a trajectory, treat the unmatched detections as the new trajectories, and ultimately produce the final tracking results $T_t$.

![image-20240530120858787](https://p.ipic.vip/ug2cct.png)

<h2 align = "center">
Contributions
</h2>

- **Dual-Domain Integrated Attention (DIA)** is proposed to enhance the detection and feature embedding of smallsized, blurred, and occluded objects in videos captured by drone.

- **Motion-Driven Association (MDA)** is proposed for robust data association, which includes AFS to refine the trajectory appearance and DMP to predict the object position considering the simultaneous motions of the drone and the objects.
- Extensive evaluations on the Visdrone2019-MOT and UAVDT datasets demonstrate that DroneMOT outperforms **the state-of-the-art methods for multiobject tracking on drones**.

<h2 align = "center">
Evaluations
<h2>


![image-20240530120945596](https://p.ipic.vip/nsesx9.png)

<img src="https://p.ipic.vip/fx8cu5.png" alt="image-20240530121007711" style="zoom:50%;" />

<img src="https://p.ipic.vip/te370t.png" alt="image-20240530121121040" style="zoom: 67%;" />

<img src="https://p.ipic.vip/tsvrw6.png" alt="image-20240530121121031" style="zoom: 67%;" />


<h2 align = "center">
Acknowledgment 
</h2>
This work was supported in part by the National Natural Science Foundation of China Grant No. 61972404, 12071478; Public Computing Cloud, Renmin University of China; Blockchain Laboratory, Metaverse Research Center, Renmin University of China.






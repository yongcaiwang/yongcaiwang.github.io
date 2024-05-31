<h2 align = "center">
ColSLAM: A Versatile Collaborative SLAM System for Mobile Phones Using Point-Line Features and Map Caching
</h2>
<h4 align = "center" >
Proceedings of <a href="https://dl.acm.org/doi/abs/10.1145/3581783.3611995"> ACM MM 2023 </a>
</h4>

Wanting Li^1^, Yongcai Wang^1,*^,  Yongyu Guo^1^, Shuo Wang^1^, Yu Shao^1^, Xuewei Bai^1^, Xudong Cai^1^, Qiang Ye^2^, Deying Li^1^

^1^ School of Information, Renmin University of China, Beijing, 100872 

^2^ Department of Computer Science, Dalhousie University, Halifax, Canada



<center>
  <a href="colslam.pdf"><img height= "50" src="https://p.ipic.vip/f50s58.png" alt="image-20240529183359317"  /> 
  </a>
  <a href="#">
  <img height= "50" src="https://p.ipic.vip/exxqen.png" alt="image-20240529183422179"/>
  </a>  
  <a href="#">
  <img height= "50" src="https://p.ipic.vip/c13w3s.png" alt="image-20240529183517490"/>
  </a> 
</center>




<video controls="controls" autoplay="autoplay" src="colSLAM.mp4" type="video/mp4"></video>


<h2 align = "center">
Overview 
</h2>
In this paper, we propose a scalable and robust collaborative SLAM system, point-line-based Collaborative SLAM (ColSLAM). Technically, ColSLAM includes two innovative features that help achieve satisfactory scalability and robustness. First, a mapping cacher (MC) is designed for each agent on the server, which uses global keyframes to detect loop closures, updates the cached local map, and quickly responds to the agent’s pose drifts. With MC, each agent’s local pose is corrected using global knowledge in real-time. Secondly, to improve the robustness performance, ColSLAM employs point-line-fusion-based Visual Inertial Odometry (VIO), point-line-fusion-based NetVLAD loop detection, and an enhanced geometric verification and relative pose calculation method called PNPL. Empirical evaluations based on the EuRoc dataset and real degenerate environments demonstrate that  ColSLAM outperforms the existing collaborative SLAM systems in terms of  accuracy, robustness, and scalability.

<h2 align = "center">
System Architecture 
</h2>
Each agent uses its own sensor information to perform points and lines VIO and then transmits the results to the server through a communication module. The server stores the information of the agent through map caching. The server performs place recognition, map fusion, and optimization based on point and line features. Then, the pose drifts are transmitted to the agents for correcting the agents’ local drifts.



![image-20240529163949630](https://p.ipic.vip/yhov6t.png)

<h2 align = "center">
Feature
</h2>


-   **Map caching**: ColSLAM includes a two-stage asynchronous optimization method for cached sub-graph (CSG) optimization and global map optimization. This method ensures real- time responses to agents while taking accuracy and commu- nication efficiency into consideration, which significantly improves the scalability of collaborative SLAM.

-   **Robust point-line features**: ColSLAM redesigns the whole collaborative SLAM framework to utilize point-line features. Technically, ColSLAM includes point-line-based VIO on the agents and the point-line fusion-based NetVLAD method to conduct loop detection on the server. Robust features are indispensable for multi-agent collaboration.

-   **Collaborative loop detection**: With ColSLAM, we use an enhanced geometric verification and relative pose calculation method, called PNPL, to further improve the robustness and accuracy of the system.

<h2 align = "center">
Evaluations
<h2>


![image-20240529164455777](https://p.ipic.vip/5vuqvm.png)

<img width="500" src="https://p.ipic.vip/drqths.png" alt="image-20240529164545366" style="zoom:67%;" />

<img width="500"  src="https://p.ipic.vip/3g4qab.png" alt="image-20240529164654622" style="zoom:67%;" />

<img width="500" src="https://p.ipic.vip/r9c0hx.png" alt="image-20240529164735546" style="zoom:67%;" />

<img width="500"  src="https://p.ipic.vip/d3vxte.png" alt="image-20240529164843822" style="zoom: 67%;" />

<h2 align = "center">
Bibtex
</h2>
```tex
@inproceedings{colslam2023acmmm,
    author = {Li, Wanting and Wang, Yongcai and Guo, Yongyu and Wang, Shuo and Shao, Yu and Bai, Xuewei and Cai, Xudong and Ye, Qiang and Li, Deying},
    title = {ColSLAM: A Versatile Collaborative SLAM System for Mobile Phones Using Point-Line Features and Map Caching},
    year = {2023},
    isbn = {9798400701085},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    url = {https://doi.org/10.1145/3581783.3611995},
    doi = {10.1145/3581783.3611995},
    booktitle = {Proceedings of the 31st ACM International Conference on Multimedia},
    pages = {9032–9041},
    numpages = {10},
    location = {, Ottawa ON, Canada, },
    series = {MM '23}
    }
```


<h2 align = "center">
Acknowledgment 
</h2>
This work was supported in part by the National Natural Science Foundation of China Grant No. 61972404, 12071478; Public Computing Cloud, Renmin University of China; Blockchain Laboratory, Metaverse Research Center, Renmin University of China.






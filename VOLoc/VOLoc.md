<h2 align = "center">
VOLoc: Visual Place Recognition by Querying Compressed Lidar Map
</h2>
<h4 align = "center" >
Proceedings of <a href="https://2024.ieee-icra.org/">ICRA 2024</a> </a>
</h4>


Xudong Cai^1^, Yongcai Wang^1,*^,  Zhe Huang^1^, Yu Shao^1^, Deying Li^1^

^1^ School of Information, Renmin University of China, Beijing, 100872 



<center>
  <a href="VOLoc.pdf"><img height= "50" src="https://p.ipic.vip/f50s58.png" alt="image-20240529183359317"  /> 
  </a>
  <a href="https://github.com/Master-cai/VOLoc">
  <img height= "50" src="https://p.ipic.vip/exxqen.png" alt="image-20240529183422179"/>
  </a>  
  <a href="#">
  <img height= "50" src="https://p.ipic.vip/c13w3s.png" alt="image-20240529183517490"/>
  </a> 
</center>





<video controls="controls" autoplay="autoplay" src="VOLoc.mp4" type="video/mp4"></video>


<h2 align = "center">
Overview 
</h2>
The availability of city-scale Lidar maps enables the potential of city-scale place recognition using mobile cam- eras. However, the city-scale Lidar maps generally need to be compressed for storage efficiency, which increases the difficulty of direct visual place recognition in compressed Lidar maps. This paper proposes VOLoc, an accurate and efficient visual place recognition method that exploits geometric similarity to directly query the compressed Lidar map via the real-time cap- tured image sequence. In the offline phase, VOLoc compresses the Lidar maps using a *Geometry-Preserving Compressor* (GPC), in which the compression is reversible, a crucial requirement for the downstream 6DoF pose estimation. In the online phase, VOLoc proposes an online Geometric Recovery Module (GRM), which is composed of online Visual Odometry (VO) and a point cloud optimization module, such that the local scene structure around the camera is online recovered to build the *Querying Point Cloud* (QPC). Then the QPC is compressed by the same GPC, and is aggregated into a global descriptor by an attention- based aggregation module, to query the compressed Lidar map in the vector space. A transfer learning mechanism is also proposed to improve the accuracy and the generality of the aggregation network. Extensive evaluations show that VOLoc provides localization accuracy even better than the Lidar-to- Lidar place recognition, setting up a new record for utilizing the compressed Lidar map by low-end mobile cameras. 

<h2 align = "center">
System Architecture 
</h2>
Consider a city-scale point cloud map $\mathcal{M}$ which is collected along the city roads. The map is segmented into  segments of equal size. We compress the segmented maps for storage efficiency and setup a database,  i.e., $\mathcal{DB}=\{c_1, c_2, ..., c_N\}$, where $c_i$ is the $i$th compressed segment. A client equipped with a mono-camera queries the database using its captured images to find which segment the client is most possibly located at.

<img src="https://gitee.com/master-cai/oss/raw/master/blog/2024/05-31-image-20240531105642836.png" alt="image-20240531105642836" style="zoom:67%;" />

The overview of the proposed method is shown. The Lidar sub-maps are first processed by Geometry-Preserving Compressor (Section~\ref{sec:GPC}),  and are then processed by the Feature Aggregation module (Section~\ref{sec:Global Feature Aggregation}) to be converted into global descriptors $D_d=\{d_1, d_2, ..., d_N\}$.

<img src="https://gitee.com/master-cai/oss/raw/master/blog/2024/05-31-image-20240531111255434.png" alt="image-20240531111255434"  />

<h2 align = "center">
Evaluations
</h2>

![image-20240531111311324](https://gitee.com/master-cai/oss/raw/master/blog/2024/05-31-image-20240531111311324.png)

<h2 align = "center">
Visualization
</h2>
<img src="https://gitee.com/master-cai/oss/raw/master/blog/2024/05-31-image-20240531111324494.png" alt="image-20240531111324494" style="zoom:67%;" />

<img src="https://gitee.com/master-cai/oss/raw/master/blog/2024/05-31-image-20240531111347493.png" alt="image-20240531111347493" style="zoom:67%;" />


<h2 align = "center">
Bibtex
</h2>

```tex
@article{cai2024voloc,
    title   = {VOLoc: Visual Place Recognition by Querying Compressed Lidar Map},
    author  = {Xudong Cai, Yongcai Wang,  Zhe Huang, Yu Shao, Deying Li},
    journal = {arXiv preprint arXiv:2402.15961},
    year    = {2024},
}
```


<h2 align = "center">
Acknowledgment 
</h2>
This work was supported in part by the National Natural Science Foundation of China Grant No. 61972404, 12071478; Public Computing Cloud, Renmin University of China; Blockchain Laboratory, Metaverse Research Center, Renmin University of China.






<h2 align = "center">
<a href="https://doi.org/10.1109/TVCG.2024.3400822">
DMS: Low-overlap Registration of 3D Point Clouds with Double-layer Multi-scale Star-graph
</h2>
<h4 align = "center" >
<a href="https://www.computer.org/csdl/journal/tg"> IEEE Transactions on Visualization and Computer Graphics </a>
</h4>
 

Hualong Cao $^1$, Yongcai Wang^1^, Deying Li^1^

^1^School of Information, Renmin University of China, Beijing, 100872



<center>
  <a href="DMS.pdf"><img height= "50" src="https://p.ipic.vip/f50s58.png" alt="image-20240529183359317"  /> 
  </a>
  <a href="https://github.com/HualongCao/DMS">
  <img height= "50" src="https://p.ipic.vip/exxqen.png" alt="image-20240529183422179"/>
  </a>  
</center>





<video controls="controls" autoplay="autoplay" src="DMS.mp4" type="video/mp4"></video>


<h2 align = "center">
Overview 
</h2>
Registering 3D point clouds with low overlap is challenging in 3D computer vision, primarily due to difficulties in identifying small overlap regions and removing correspondence outliers. We observe that the neighborhood similarity can be utilized to detect point correspondence, and the consistent neighborhood correspondence can be used as a criterion to detect robust overlapping regions. So that a Double-layer Multi-scale Star-graph (DMS) structure is proposed to detect robust correspondences using two different types of multi-scale star-graphs. The first-layer \emph{Multi-scale Neighbor Feature Star-graphs} (MNFS) takes each point as the center and its multi-scale nearest neighbors as the leaves. The MNFS enables to establish the initial correspondence candidate set between the two point clouds based on multi-scale neighborhood topology and feature similarity. Subsequently, each pair of corresponding points find their nearest neighbors within the correspondence sets to construct a Multi-scale Matching Star-graphs (MMS) on each side, so the mutual correspondence relationships between the MMS vertices are identified. These identified mutual correspondences are  treated as vertices to construct the \emph{Multi-scale Correspondence Star-graphs (MCS)} , that indicate the relationships among the correspondences. We design edge weight and vertex weight criterion  in MCS  to detect only the robust correspondence set that has strong neighborhood consistency, so as to reject the outliers. Finally, the point cloud registration is conducted based on the detected robust correspondence. The experimental results  demonstrate clearly that the proposed DMS method exhibits superior robustness when compared to existing state-of-the-art registration algorithms.

<h2 align = "center">
System Architecture 
</h2>
Each agent uses its own sensor information to perform points and lines VIO and then transmits the results to the server through a communication module. The server stores the information of the agent through map caching. The server performs place recognition, map fusion, and optimization based on point and line features. Then, the pose drifts are transmitted to the agents for correcting the agents’ local drifts.



![1](https://p.ipic.vip/tixf7q.jpg)

<h2 align = "center">
Contributions
</h2>


-   **DMS**: DMS handles the registration problem of low-overlapping point clouds by constructing a two-level star graph. The first layer is MNFS, which selects similar points based on multi-scale neighborhood topology and feature similarity to establish initial correspondence. The second layer is MCS, which is used to evaluate the detected correspondences to reserve only robust correspondences with strong neighborhood consistency. DMS provides a novel approach to improve the accuracy and robustness of low-overlap point cloud registration.

-   **MNFS**: In order to enhance the neighborhood and feature consistency of super-points, this study designed the MNFS method, which improves the accuracy of the overall registration process while maintaining the consistency of information between super-points.

-   **MCS**: In the MCS stage, we construct the MCS by developing MMS for each point pair and identify mutual correspondences between the MMS graphs. Then the mutual correspondences are treated as vertices to generate MCS graphs, which are used to identify correspondences that meet neighborhood consistency criteria. This process ultimately filters and refines the correspondences, leading to an accurate and efficient point registration within the MCS framework.

<h2 align = "center">
Evaluations
<h2>


![2](https://p.ipic.vip/knrddw.png)

<img src="https://p.ipic.vip/1jva0a.jpg" alt="3" style="zoom:67%;" />

<img src="https://p.ipic.vip/k6smwu.jpg" alt="4" style="zoom:67%;" />

<img src="https://p.ipic.vip/gwindp.jpg" alt="5" style="zoom:67%;" />

<h2 align = "center">
Bibtex
</h2>
```tex
@ARTICLE{DMS,
  author={Cao, Hualong and Wang, Yongcai and Li, Deying},
  journal={IEEE Transactions on Visualization and Computer Graphics}, 
  title={DMS: Low-overlap Registration of 3D Point Clouds with Double-layer Multi-scale Star-graph}, 
  year={2024},
  volume={},
  number={},
  pages={1-16},
  doi={10.1109/TVCG.2024.3400822}}
```


<h2 align = "center">
Acknowledgment 
</h2>
Dr. Wang is supported in part by the National Natural Science Foundation of China Grant No. 61972404, Public Computing Cloud, Renmin University of China, and the Blockchain Lab. School of Information, Renmin University of China.  Dr. Li is supported in part by the National Natural Science Foundation of China Grant No. 12071478. Hualong Cao is supported by the Fundamental Research Funds for the Central Universities, and the Research Funds of Renmin University of China Grant No. 23XNH146, and Supported by the Outstanding Innovative Talents Cultivation Funded Programs 2023 of Renmin University of China.






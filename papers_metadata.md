# IEEE Xplore Papers Metadata

*Generated on: 2026-06-29 19:28:00*

---

## 1. STGBD-Net: Spatio-Temporal Gradient Basis Decomposition Network for Infrared Small Target Detection
- **URL**: https://ieeexplore.ieee.org/document/11554108
- **Authors**: Chen Hu, Mingyu Zhou, Shuai Yuan, Hongbo Hu, Zhenming Peng, Tian Pu, Xiying Li
- **Publication Year**: 2026
- **DOI**: 10.1109/TGRS.2026.3701189

### Abstract
A key challenge in infrared small target detection (IRSTD) is that weak target signal responses are easily obscured by strong background clutter, frequently resulting in missed detections. While traditional gradient-based methods attempt to capture fine details, their robustness is limited by the static fusion of multidirectional gradient features. In this article, we rethink feature fusion from the perspective of Basis Decomposition Theory and propose a novel framework that reformulates the process into an explicit and adaptive decomposition-and-reconstruction paradigm. Specifically, we introduce the basis decomposition module (BDM) and its specialized variant, the gradient decomposition module (GDM) for IRSTD. GDMs treat the normalized gradient features as basis vectors to reconstruct a new feature, thereby maintaining detailed structures and highlighting infrared small targets. By integrating GDMs into a lightweight three-stage U-Net, we develop two unified architectures: the spatial gradient basis decomposition network for single-frame detection and the spatio-temporal gradient basis decomposition network for multiframe scenarios. Extensive experiments demonstrate that our networks achieve state-of-the-art (SOTA) performance across multiple benchmarks, offering a superior balance between detection accuracy and computational efficiency. Our codes will be made public at: <uri xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">https://github.com/greekinRoma/IRSTD_HC_Platform</uri>

### Keywords
- **IEEE Keywords**: Modeling, Modules (abstract algebra), Object detection, Educational institutions, Signal detection, Conferences, Computer vision, Computers, Kernel, Personal digital devices
- **Index Terms**: Small Target, Spatiotemporal Network, Basis Of Decomposition, Infrared Small Target, Computational Efficiency, Vector-based, Spatial Gradients, Spatial Network, Gradient-based Methods, Background Clutter, Gradient Features, Spatial Basis, Spatial Decomposition, Spatial Dimensions, Intersection Over Union, False Alarm, Spatial Model, Temporal Information, Spatial Domain, Temporal Modulation, Attention Network, Dynamic Background, Channel Dimension, Complex Background, Gradient Information, Frames Per Second, Local Contrast, Input Feature Vector, Gradient Operator
- **Author Keywords**: Basis decomposition, basis decomposition module (BDM), gradient decomposition module (GDM), infrared small target detection (IRSTD), three-stage U-Net

---

## 2. A Graph-Based Framework for Detecting Small Noisy Targets: Theory and Analysis
- **URL**: https://ieeexplore.ieee.org/document/11463567
- **Authors**: Nicholas Bampton, Tian J. Ma, Minh N. Do
- **Publication Year**: 2026
- **DOI**: 10.1109/ICASSP55912.2026.11463567

### Abstract
Small target detection, particularly in noisy environments, is a difficult task due to their limited size, lack of distinctive features, and the presence of cluttered, complex backgrounds. Dynamic programming offers efficient solutions to this problem through algorithms like Viterbi and Pixel Aggregation. These approaches often rely on iterative maximization steps, which have traditionally limited the analytical tools available for their study. In this paper, we present a robust theoretical framework for this class of algorithms and establish rigorous convergence results for error rates under mild assumptions. By representing their structure as a graph, we recast these algorithms as longest-path problems on directed acyclic graphs. We further depart from traditional analysis by modeling error probabilities as a function of distance from the target, allowing us to construct a relationship between uncertainty in location and uncertainty in existence. Based on this framework, we introduce a novel subset of dynamic programming algorithms (LPA-NBM) that utilizes the similarity between sequential state observations rather than the individual observations themselves, making it an appropriate tool for identifying targets that have difficult to ascertain features.

### Keywords
- **IEEE Keywords**: Filtering, Filters, MIMICs, Millimeter wave integrated circuits, Monolithic integrated circuits, Circuits and systems, Pixel, Protocols, HTTP, Videos
- **Index Terms**: Small Target, Distance Function, Dynamic Programming, State Observer, Position Uncertainty, Dynamic Programming Algorithm, Mild Assumptions, False Positive, Computational Efficiency, State Space, Gaussian Noise, Edge Weights, Target State, Low Signal-to-noise Ratio, Background Model, Human Visual System, Actual Radius, Target Amplitude
- **Author Keywords**: small target detection, low signal-to-noise ratio, target tracking, dynamic programming

---

## 3. Deep Unfolding Residual Decomposition for Infrared Small Target Detection
- **URL**: https://ieeexplore.ieee.org/document/11523120
- **Authors**: Fan Hao, Feng Wei, Feng Zhou, Zhipeng Wang, Shichao Yao, Xueyan Yang, Zongfang Ma
- **Publication Year**: 2026
- **DOI**: 10.1109/TGRS.2026.3694155

### Abstract
Detecting infrared dim small targets remains a challenging task due to strong background interference and low signal-to-clutter ratio (SCR), which frequently results in target features being submerged by clutter. Furthermore, existing methods often struggle to strike a balance between physical interpretability and advanced feature representation. To address these limitations, this article proposes a deep unfolding residual decomposition (DURD) method based on a novel dual-branch framework. First, an adaptive structured decomposition (ASD) module is proposed, which unfolds iterative optimization into a deep neural network. The ASD module leverages an implicit low-rank subspace projection and an adaptive structured sparse perception mechanism to separate high-quality physical sparse priors from low-rank background components. Second, to further exploit deep semantic representations and suppress high-frequency clutter, a residual-driven multiscale encoder–decoder (RMED) is designed. Using physically constrained residual features as input, RMED emphasizes target regions while suppressing background interference. Through full-scale feature aggregation and deep supervision mechanisms, it hierarchically extracts robust multiscale semantic representations. Finally, a dual-branch cooperative fusion (DCF) module is developed to integrate the outputs of both branches. The DCF employs a learnable gating factor to adaptively balance the contributions of physical sparse priors and deep semantic features, thereby achieving a complementary and discriminative enhancement for infrared small target detection. Extensive experiments demonstrate that the proposed DURD significantly enhances the detection accuracy in complex scenarios. The code is available at <uri xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">https://github.com/haofan72/DURD</uri>

### Keywords
- **IEEE Keywords**: Ranking (statistics), Modeling, Signal detection, Object detection, Modules (abstract algebra), Optimization, Personal digital devices, Interference, Matrices, Robustness
- **Index Terms**: Deep Network, Deep Neural Network, Detection Accuracy, Feature Representation, Deep Features, Semantic Features, Physical Interpretation, Semantic Representations, Background Interference, Residual Feature, Deep Representation, Background Components, Subspace Projection, Deep Learning, Superior Performance, Computational Efficiency, Quantitative Results, Infrared Imaging, Detection Performance, Intersection Over Union, Sparse Component, Low-rank Decomposition, Multi-scale Features, Feature Refinement, Learnable Parameters, False Alarm, Non-negative Matrix Factorization, Sparse Representation, Physical Constraints, Residual Block
- **Author Keywords**: Decomposition, deep supervision, deep unfolding, infrared small target, multiscale

---

## 4. MFEFNet: An Efficient Network for Infrared Small Target Detection With Multiview Feature Extraction and Multiscale Attention Fusion
- **URL**: https://ieeexplore.ieee.org/document/11482805
- **Authors**: Liu Zhang, Zongchen Zhao, Xueying Lv, Xuanyun Zhang, Wenhua Wang, Jiabao Zhang
- **Publication Year**: 2026
- **DOI**: 10.1109/JSTARS.2026.3685006

### Abstract
Infrared small target detection (IRSTD) remains a core challenge in remote sensing, mainly due to low signal-to-noise ratios, small target sizes, background interference, and large-scale variations. Although existing methods have achieved progress, they still suffer from limited representation ability of conventional convolutions, weak feature enhancement, and insufficient multiscale feature fusion, which restrict detection performance and practical application. To alleviate these issues, this article introduces a dedicated multiaspect feature extraction and fusion network (MFEFNet). The proposed framework systematically addresses the above challenges via three innovative components: the multishape receptive field extraction module (MSRFEM), the spatial-channel-global-local joint re-extraction module (SCGLJRM), and the multiscale cross-attention mechanism (MSCAM). Specifically, MSRFEM leverages dilated deformable convolutions and the Res2 architecture to adaptively capture multiscale and multishape target characteristics as well as locally correlated features. SCGLJRM enhances global context modeling across spatial and channel dimensions by aggregating complementary local-global information through a cascade of local spatial-local channel, local spatial-global channel, and global spatial-local channel submodules. MSCAM mitigates the feature fusion imbalance in typical transformer-based cross-attention by performing correlation matrix transposition and fusion before integrating with feature maps, thereby strengthening the mutual enhancement of unique and shared information across different scales. Notably, MFEFNet breaks the constraints of fixed input image resolution, supporting flexible training and inference with arbitrary image sizes. Extensive experiments conducted on SIRST, IRSTD-1K, and NUDT-SIRST datasets consistently verify that MFEFNet achieves superior detection accuracy over numerous state-of-the-art methods and maintains strong generalization ability under complex backgrounds, demonstrating its effectiveness and superiority.

### Keywords
- **IEEE Keywords**: Aerospace and electronic systems, Space technology, Payloads, Filtering, Filters, Integrated circuits, System-on-chip, Circuits and systems, Pixel, Digital images
- **Index Terms**: Small Target, Multi-view Feature Extraction, Information Exchange, Detection Accuracy, Image Size, Detection Performance, Receptive Field, Feature Fusion, Multi-scale Features, Channel Dimension, Target Size, Complex Background, Superior Accuracy, Local Channel, Feature Enhancement, Fusion Network, Superior Detection, Multi-scale Feature Fusion, Deformable Convolution, Conventional Convolution, Target Features, Global Information, Data-driven Methods, Self-attention Mechanism, Local Information, Attention Mechanism, Target Information, Background Suppression, Small Objects, Visible Images
- **Author Keywords**: Infrared small target detection (IRSTD), multiscale mutual attention mechanism, multiscale shape receptive fields, spatial-channel information extraction

---

## 5. Memory-Enhanced Spatio-Temporal Fusion for Multiframe Infrared Small Target Detection
- **URL**: https://ieeexplore.ieee.org/document/11501253
- **Authors**: Meihong Zhang, Liang Chang, Dan Zeng, Rui Gao
- **Publication Year**: 2026
- **DOI**: 10.1109/LGRS.2026.3688799

### Abstract
Multiframe infrared small target detection (MISTD) is challenging due to complex target motion and severe background interference. Existing methods typically rely on global optical flow estimation or locally constrained motion compensation, with fixed upsampling and limited background suppression, hindering accurate temporal alignment and fine target preservation. To address these issues, we propose DCPNet, a unified memory-enhanced spatio-temporal fusion framework for MISTD. In the encoder, a deformable spatio-temporal module (DSTM) enhances inter-frame consistency. In the decoder, a content-guided adaptive upsampling (CGAU) module preserves weak target structures, while a prototype-aware memory reconstruction (PMR) module enhances target-background separability. Experiments on two datasets show that DCPNet outperforms 23 state-of-the-art methods on pixel- and target-level metrics, achieving a notable 5% IoU gain and demonstrating its robustness in complex scenes.

### Keywords
- **IEEE Keywords**: Feeds, Filtering, Filters, Pixel, Electronic mail, Digital images, Receivers, LoRa, Videos, Wireless Access in Vehicular Environments
- **Index Terms**: Spatiotemporal Fusion, Intersection Over Union, Weak Structure, Complex Motion, Background Interference, Motion Compensation, Weak Targets, Reconstruction Module, Spatiotemporal Framework, Decoding, Infrared Imaging, Softmax, Data-driven Methods, Complex Background, Local Assembly, Local Correlation, Global Motion, Improve Detection Performance, Temporal Aggregation, Background Pattern, Decoder Features
- **Author Keywords**: Adaptive upsampling, deformable alignment, memory reconstruction, multiframe infrared small target detection (MISTD)

---

## 6. MIST: A Benchmark and Baseline for Multi-Frame Infrared Small Target Detection in Complex Motion
- **URL**: https://ieeexplore.ieee.org/document/11511399
- **Authors**: Rui Gao, Meihong Zhang, Gongyang Li, Guanyi Li, Kai Zhao, Xianchao Zhang, Dan Zeng
- **Publication Year**: 2026
- **DOI**: 10.1109/TIP.2026.3689420

### Abstract
Motion cues play a vital role in multi-frame infrared small target detection (MISTD). However, most targets in existing datasets exhibit regular and slow motion, which cannot reflect the complex and diverse motion patterns in real-world scenarios. This biased data distribution makes recent data-driven methods highly rely on simplified motion assumptions that tend to fail in irregular or fast motion, resulting in noisy feature representations cluttered with target-irrelevant factors. Hence, we stress that methods for MISTD should also work when targets are in complex motion. To enable this research, we propose a large-scale dataset called MIST for airborne infrared detection scenarios. The dataset is built on a synthetic data engine that models variations in pose, size, and intensity of moving targets while seamlessly blending them into real backgrounds for physical, geometric, and visual realism. Targets in MIST exhibit low signal-to-clutter ratios and complex motion, making it a promising yet challenging benchmark for developing algorithms focused on motion analysis. To tackle the challenges of MIST, we develop MISTNet, a robust baseline based on the Information Bottleneck theory. To handle irregular and fast motion, we propose a shifted neighborhood compensation block to efficiently model multi-scale correspondences for implicit motion compensation. To distill compact representations free from irrelevant cues, we design a progressive distillation decoder to hierarchically filter out redundancy while preserving target-relevant information. We benchmark 31 state-of-the-art methods and find that their performance on MIST drops significantly compared with that on the widely used NUDT-MIRSDT dataset. Our MISTNet outperforms all other methods by a large margin, with an over 6% gain in the IoU metric, demonstrating its superiority. The dataset, code, and model weights are available at <uri xmlns:mml="http://www.w3.org/1998/Math/MathML" xmlns:xlink="http://www.w3.org/1999/xlink">https://github.com/GR-ray/MIST</uri>

### Keywords
- **IEEE Keywords**: Missiles, Feeds, Filtering, Filters, Circuits and systems, Modulation, Pixel, LoRa, Videos, Communications technology
- **Index Terms**: Small Target, Complex Motion, Complex Patterns, Intersection Over Union, Real-world Scenarios, Data-driven Methods, Motion Analysis, Motion Patterns, Simple Assumption, Slow Motion, Fast Motion, Motion Compensation, Motion Cues, Simple Motion, Detection Scenario, Information Bottleneck, Irregular Motion, Mutual Information, False Alarm, Receptive Field, Multiple Frames, Temporal Model, Bezier Curve, Optical Flow, Proportion Of Sequences, Target Template, Successive Frames, Precise Annotation, Frame Features, Irrelevant Factors
- **Author Keywords**: Multi-frame infrared small target detection, synthetic data, complex motion, shifted neighborhood compensation block, progressive distillation decoder, information bottleneck

---

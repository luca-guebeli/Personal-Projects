# Models

This folder tracks model experiments, conversion notes, and deployment artifacts for STM32N6.

Large trained models and datasets should usually stay outside the repo. Commit small configs, scripts, model cards, and tiny sample artifacts only when they are useful for reproducibility.

## Candidate First Models

### Vision
- Image classification on a small class set
- Person/object detection at low resolution
- Simple scene classifier for camera pipeline validation
- Center-object binary segmentation for outline generation

### Audio
- Keyword spotting
- Clap/knock detection
- Sound event classification

## Center-Object Outline Model

The main vision idea is to outline the object near the center of the camera frame. That is best treated as segmentation, not only detection:

- Detection gives boxes.
- Segmentation gives a mask.
- A mask can be post-processed into an outline.

The first useful model target is a small binary segmentation network:

- Input: resized RGB frame or center crop, likely 160x160 or 224x224
- Output: binary mask for foreground object vs background
- Post-processing: threshold mask, keep component nearest frame center, smooth, trace contour
- Deployment goal: INT8 model converted through ST Edge AI tooling for STM32N6

Avoid starting with a general-purpose segmentation model that tries to understand every object category. A narrower dataset of centered desk objects or electronics parts will be much easier to train, debug, and deploy.

The PC training scaffold lives in:

```text
training/center_object_segmentation/
```

It starts with a stronger residual U-Net-style model for learning the task well on the PC. Once the dataset and labels are good, use the trained model as a teacher or baseline, then make a smaller STM32N6 deployment model.

## Model Notes Template

For each model, record:

- Source framework: TensorFlow, Keras, PyTorch, ONNX, or TFLite
- Input shape and preprocessing
- Output classes
- Quantization method
- ST Edge AI tooling version
- Target memory footprint
- Measured inference latency
- Accuracy or qualitative test results

## References

- [STM32N6 AI ecosystem - STMicroelectronics](https://www.st.com/en/development-tools/stm32n6-ai.html)

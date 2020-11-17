## Training on AWS
Nvidia Deep Learning AMI: `ami-0384cb16509f0e03b`

#### Cloud instance set-up
Add SSH ingress rules and open the ports for inbound and outbound traffic
```
aws ec2 authorize-security-group-ingress --group-id sg-******* --protocol tcp --port 22 --cidr 0.0.0.0/0
aws ec2 authorize-security-group-ingress --group-id sg-******* --protocol tcp --port 8888 --cidr 0.0.0.0/0
```

Start a `g4dn.2xlarge` instance with Nvidia deep learning AMI and appropriate security group
```
aws ec2 run-instances --image-id ami-0384cb16509f0e03b --instance-type g4dn.2xlarge --security-group-ids sg-******* --associate-public-ip-address --key-name key-name
```

Obtain server address
```
aws ec2 describe-instances | grep ec2
```

SSH into the cloud instance
```
ssh -i "path/to/key/key-name.pem" ubuntu@ec2-xx-xxx-xxx-xx.us-regionname-x.compute.amazonaws.com
```

Install AWS CLI if new instance
```
sudo apt install awscli
```

#### Training
Grab data from S3 Bucket
```
aws s3 cp s3://your/bucket/address/data ./data --recursive
aws s3 cp s3://your/bucket/address/Dockerfile.cloud.yolov5 .
```

Dockerfile.cloud.yolov5
```
# Start FROM Nvidia PyTorch image https://ngc.nvidia.com/catalog/containers/nvidia:pytorch
FROM nvcr.io/nvidia/pytorch:20.07-py3
#20.03 version with pytorch build version 1.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN git clone https://github.com/ultralytics/yolov5

WORKDIR /usr/src/app/yolov5
```

Build docker image
```
docker build --tag yolov5cloud -f Dockerfile.cloud.yolov5 .
```

Run docker container
- mount local /data directory to /data in docker: this directory
- the mounted directory will be used in the data flag in the training command
```
docker run --ipc=host --name yolov5cloud --rm --privileged --gpus all -v $PWD/data:/data -v /tmp:/tmp -p 8888:8888 -p 6006:6006 -ti yolov5cloud
```

Create custom `model.yaml` and `data.yaml` file
```sh
vim /data/data.yaml  # change train and validation image path in data.yaml to /data/train & /data/validate
cp models/yolov5s.yaml /data  # copy the model.yaml file from yolov5 repo to /data
vim /data/yolov5s.yaml    # change number of classes in the model.yaml file to match use case
mv /data/yolov5s.yaml /data/custom_model.yaml  # rename customized model.yaml file
```

Training  
- place `data.yaml` under the data flag; this tells `train.py` where to find training images
- place `custom_model.yaml` under cfg flag; this specifies model configuration
- place pre-trained base weights under weights flag for transfer learning; use ' ' if training from scratch
```
python3 train.py --img 416 --batch 16 --epochs 200 --data /data/data.yaml --cfg /data/custom_model.yaml --weights yolov5s.pt --name custom_object --cache

python3 train.py --img 416 --batch 16 --epochs 200 --data /data/data.yaml --cfg /data/custom_model.yaml --weights yolov5m.pt --name custom_object --cache
```

Output trained weights
```
cp -f runs/expX_output_folder /data
...
```

Exit the container and sync trained weights from EC2 to S3
```
aws s3 sync . s3://your/bucket/address/data
```

Dockerfile.nx.yolov5
```
# FROM nvcr.io/nvidia/l4t-ml:r32.4.2-py3
FROM nvcr.io/nvidia/l4t-ml:r32.4.3-py3

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN git clone https://github.com/ultralytics/yolov5

WORKDIR /usr/src/app/yolov5

RUN apt update && apt install -y libffi-dev python3-pip curl unzip python3-tk libopencv-dev python3-opencv
RUN pip3 install -U gsutil pyyaml tqdm cython torchvision   
RUN apt install -y python3-scipy python3-matplotlib python3-numpy
RUN pip3 install git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI
```

Build docker image on the edge device
```
docker build --tag yolov5nx -f Dockerfile.nx.yolov5 .
```

#### Inference using live camera feeds
Enable X and Start the NX container on the edge device for detection
```
xhost +
docker run --rm --privileged --runtime nvidia -v $PWD/data:/data -e DISPLAY -v /tmp:/tmp -ti yolov5nx python3 detect.py --source 0 --weights /data/best.pt --img 416 --conf 0.4 --source 0
```

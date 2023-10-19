import sys
sys.path.insert(0, './yolov5')

from yolov5.utils.google_utils import attempt_download
from yolov5.models.experimental import attempt_load
from yolov5.utils.datasets import LoadImages, LoadStreams,LoadStreams_Mjpeg
from yolov5.utils.general import check_img_size, non_max_suppression, scale_coords, \
    check_imshow
from yolov5.utils.torch_utils import select_device, time_synchronized
from deep_sort_pytorch.utils.parser import get_config
from deep_sort_pytorch.deep_sort import DeepSort
import argparse
import os
import platform
import shutil
import time
from pathlib import Path
import cv2
import torch
import torch.backends.cudnn as cudnn
import numpy as np
class optt:
    yolo_weights = 'yolov5/weights/yolov5s.pt'
    deep_sort_weights = 'deep_sort_pytorch/deep_sort/deep/checkpoint/ckpt.t7'
    
    # source = "rtsp://192.168.8.92/live_stream"
    source = "http://192.168.8.92/mjpeg_stream"
    # source = "0"
    output = 'output'
    img_size = 640
    conf_thres = 0.4
    iou_thres = 0.5
    fourcc = 'mp4v'
    device = ''
    show_vid = True
    save_vid = False
    save_txt = False
    classes = [0]
    agnostic_nms = False
    augment = False
    evaluate = False
    config_deepsort = "deep_sort_pytorch/configs/deep_sort.yaml"
    Mjpeg_mode = True
class Tracker:
    palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)
    opt = optt()
    avg_center = [320,320]
    
    def __init__(self,running,timeing,conn):
        self.opt.img_size = check_img_size(self.opt.img_size)
        self.run = running
        self.timing = timeing
        self.conn = conn
    def calculate_weights(self,outputs, k=3):
        min_id = np.min(outputs[:,-1])
        normalized_ids = outputs[:, -1] - min_id + 1
        weights = np.exp(-k * normalized_ids)
        return weights
    
    def xyxy_to_xywh(self, *xyxy):
        # implement function body as before
        bbox_left = min([xyxy[0].item(), xyxy[2].item()])
        bbox_top = min([xyxy[1].item(), xyxy[3].item()])
        bbox_w = abs(xyxy[0].item() - xyxy[2].item())
        bbox_h = abs(xyxy[1].item() - xyxy[3].item())
        x_c = (bbox_left + bbox_w / 2)
        y_c = (bbox_top + bbox_h / 2)
        w = bbox_w
        h = bbox_h
        return x_c, y_c, w, h

    def xyxy_to_tlwh(self, bbox_xyxy):
        # implement function body as before
        tlwh_bboxs = []
        for i, box in enumerate(bbox_xyxy):
            x1, y1, x2, y2 = [int(i) for i in box]
            top = x1
            left = y1
            w = int(x2 - x1)
            h = int(y2 - y1)
            tlwh_obj = [top, left, w, h]
            tlwh_bboxs.append(tlwh_obj)
        return tlwh_bboxs

    def compute_color_for_labels(self, label):
        # implement function body as before
        color = [int((p * (label ** 2 - label + 1)) % 255) for p in self.palette]
        return tuple(color)
    def draw_boxes(self, img, bbox, identities=None, offset=(0, 0)):
        # implement function body as before
        for i, box in enumerate(bbox):
            x1, y1, x2, y2 = [int(i) for i in box]
            x1 += offset[0]
            x2 += offset[0]
            y1 += offset[1]
            y2 += offset[1]
            # box text and bar
            id = int(identities[i]) if identities is not None else 0
            color = self.compute_color_for_labels(id)
            label = '{}{:d}'.format("", id)
            t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 0, 1)[0]  #修改字符，原设置： 2,2
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 1)  # 修改线框为1， 原设置：3
            cv2.rectangle(img, (x1, y1), (x1 + t_size[0] + 3, y1 + t_size[1] + 4), color, -1)
            cv2.putText(img, label, (x1, y1 +
                    t_size[1] + 4), cv2.FONT_HERSHEY_PLAIN, 1, [255, 255, 255], 1) #修改 2,.,2
        return img

    def detect(self):
        opt = self.opt
        out, source, yolo_weights, deep_sort_weights, show_vid, save_vid, save_txt, imgsz, evaluate,mjpeg_mode = \
        opt.output, opt.source, opt.yolo_weights, opt.deep_sort_weights, opt.show_vid, opt.save_vid, \
            opt.save_txt, opt.img_size, opt.evaluate,opt.Mjpeg_mode
        webcam = source == '0' or source.startswith(
            'rtsp') or source.startswith('http') or source.endswith('.txt')#判断源

        # deepsort 初始化
        cfg = get_config()
        cfg.merge_from_file(opt.config_deepsort)
        attempt_download(deep_sort_weights, repo='mikel-brostrom/Yolov5_DeepSort_Pytorch')
        deepsort = DeepSort(cfg.DEEPSORT.REID_CKPT,
                            max_dist=cfg.DEEPSORT.MAX_DIST, min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
                            nms_max_overlap=cfg.DEEPSORT.NMS_MAX_OVERLAP, max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                            max_age=cfg.DEEPSORT.MAX_AGE, n_init=cfg.DEEPSORT.N_INIT, nn_budget=cfg.DEEPSORT.NN_BUDGET,
                            use_cuda=True)

        # Initialize
        device = select_device(opt.device)#选择gpu还是cpu

        # The MOT16 evaluation runs multiple inference streams in parallel, each one writing to
        # its own .txt file. Hence, in that case, the output folder is not restored
        if not evaluate:
            if os.path.exists(out):
                pass
                shutil.rmtree(out)  # delete output folder
            os.makedirs(out)  # make new output folder
        half = device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        model = attempt_load(yolo_weights, map_location=device)  # load FP32 model
        stride = int(model.stride.max())  # model stride
        imgsz = check_img_size(imgsz, s=stride)  # check img_size
        names = model.module.names if hasattr(model, 'module') else model.names  # get class names
        if half:
            model.half()  # to FP16

        # Set Dataloader
        # vid_path, vid_writer = None, None
        # Check if environment supports image displays
        if show_vid:
            show_vid = check_imshow()

        if webcam:#加载器，是web还是本地视频
            cudnn.benchmark = True  # set True to speed up constant image size inference
            if mjpeg_mode:
                dataset =  LoadStreams_Mjpeg(sources=source,img_size=imgsz,stride=stride)
            else:
                dataset = LoadStreams(source, img_size=imgsz, stride=stride)
        else:
            dataset = LoadImages(source, img_size=imgsz)

        # Get names and colors
        # names = model.module.names if hasattr(model, 'module') else model.names

        # Run inference
        if device.type != 'cpu':
            model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
        t0 = time.time()

        # save_path = str(Path(out))
        # extract what is in between the last '/' and last '.'
        # txt_file_name = source.split('/')[-1].split('.')[0]
        # txt_path = str(Path(out)) + '/' + txt_file_name + '.txt'
        #以上为设置用
        #以下为视频流处理
        while self.timing.value:
            continue 
        for frame_idx, (path, img, im0s, vid_cap) in enumerate(dataset):
            # print(dataset)
            if self.run.value == 0:
                break
            # print(frame_idx)
            img = torch.from_numpy(img).to(device)
            img = img.half() if half else img.float()  # uint8 to fp16/32
            img /= 255.0  # 0 - 255 to 0.0 - 1.0
            if img.ndimension() == 3:
                img = img.unsqueeze(0)
            # Inference
            # t1 = time_synchronized()
            pred = model(img, augment=opt.augment)[0]#将图片传入模型进行预测，返回预测结果
            # 用非最大值抑制NMS 过滤掉冗余检测结果
            pred = non_max_suppression(
                pred, opt.conf_thres, opt.iou_thres, classes=opt.classes, agnostic=opt.agnostic_nms)
            # t2 = time_synchronized()

            # Process detections
            for i, det in enumerate(pred):  # detections per image
                
                if webcam:  # batch_size >= 1
                    p, s, im0 = path[i], '%g: ' % i, im0s[i].copy()
                else:
                    p, s, im0 = path, '', im0s

                s += '%gx%g ' % img.shape[2:]  # print string
                # save_path = str(Path(out) / Path(p).name)
                if det is not None and len(det):#如果检测到目标，对每个目标的检测结果进行处理
                    # Rescale boxes from img_size to im0 size
                    det[:, :4] = scale_coords(
                        img.shape[2:], det[:, :4], im0.shape).round()

                    # # Print results
                    # for c in det[:, -1].unique():
                    #     n = (det[:, -1] == c).sum()  # detections per class
                    #     s += '%g %ss, ' % (n, names[int(c)])  # add to string

                    xywh_bboxs = []
                    confs = []

                    # Adapt detections to deep sort input format
                    for *xyxy, conf, cls in det:
                        #目标边界框 检测结果置信度 目标类别
                        # to deep sort format
                        x_c, y_c, bbox_w, bbox_h = self.xyxy_to_xywh(*xyxy)
                        xywh_obj = [x_c, y_c, bbox_w, bbox_h]
                        xywh_bboxs.append(xywh_obj)
                        confs.append([conf.item()])

                        # bbox_center = (x_c,y_c)
                        # print(f'中心位置：{bbox_center}')
                    xywhs = torch.Tensor(xywh_bboxs)
                    confss = torch.Tensor(confs)

                    # pass detections to deepsort得到捕获的目标
                    outputs = deepsort.update(xywhs, confss, im0)                
                    # draw boxes for visualization
                    if len(outputs) > 0:
                        # print(outputs)
                        #更新目标点位置
                        center_x = (outputs[:,0]+outputs[:,2])/2
                        center_y = (outputs[:,1]+outputs[:,3])/2

                        weights = self.calculate_weights(outputs)
                        avg_center_x = np.average(center_x,weights = weights)
                        avg_center_y = np.average(center_y,weights = weights)
                        
                        hei,wid ,_= im0.shape
                        min_id_index = np.argmin(outputs[:,-1])
                        message = [[wid,hei],[avg_center_x,avg_center_y],[outputs[min_id_index,0],\
                            outputs[min_id_index,1],outputs[min_id_index,2],outputs[min_id_index,3]]]
                        self.conn.send(message)
                        # print(message)
                        # print("画面中心位置：",avg_center_x,",",avg_center_y) 
                        self.avg_center[0] = avg_center_x
                        self.avg_center[1] = avg_center_y
                        # 画出识别框
                        bbox_xyxy = outputs[:, :4]
                        identities = outputs[:, -1]
                        self.draw_boxes(im0, bbox_xyxy, identities)

                        #画出目标点位置
                        center = (int(avg_center_x), int(avg_center_y))
                        cv2.circle(im0, center, 10, (0, 255, 0), -1)
                        # to MOT format
                        # tlwh_bboxs = self.xyxy_to_tlwh(bbox_xyxy)

                        # Write MOT compliant results to file
                        # if save_txt:
                        #     for j, (tlwh_bbox, output) in enumerate(zip(tlwh_bboxs, outputs)):
                        #         bbox_top = tlwh_bbox[0]
                        #         bbox_left = tlwh_bbox[1]
                        #         bbox_w = tlwh_bbox[2]
                        #         bbox_h = tlwh_bbox[3]
                        #         identity = output[-1]
                        #         with open(txt_path, 'a') as f:
                        #             f.write(('%g ' * 10 + '\n') % (frame_idx, identity, bbox_top,
                        #                                         bbox_left, bbox_w, bbox_h, -1, -1, -1, -1))  # label format
                else:
                    deepsort.increment_ages()
                    message = []
                    self.conn.send(message)
                # Print time (inference + NMS)
                # print('%sDone. (%.3fs)' % (s, t2 - t1))

                # Stream results
                if show_vid:
                    cv2.imshow(p, im0)
                # Save results (image with detections)
                # if save_vid:
                #     if vid_path != save_path:  # new video
                #         vid_path = save_path
                #         if isinstance(vid_writer, cv2.VideoWriter):
                #             vid_writer.release()  # release previous video writer
                #         if vid_cap:  # video
                #             fps = vid_cap.get(cv2.CAP_PROP_FPS)
                #             w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                #             h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                #         else:  # stream
                #             fps, w, h = 30, im0.shape[1], im0.shape[0]
                #             save_path += '.mp4'

                #         vid_writer = cv2.VideoWriter(save_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))
                #     vid_writer.write(im0)

        # if save_txt or save_vid:
        #     print('Results saved to %s' % os.getcwd() + os.sep + out)
        #     if platform == 'darwin':  # MacOS
        #         os.system('open ' + save_path)

        print('Done. (%.3fs)' % (time.time() - t0),"QWQ")
        return

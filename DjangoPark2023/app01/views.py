import django
import pytz as pytz
from django.http import HttpResponse
from django.shortcuts import render
# from datetime import datetime
import datetime as datetime
from app01 import models
from .models import vip_uer,car_record
from aip import AipOcr
from django.utils import timezone
# Create your views here.

def Recharge(request):
    if request.method == 'POST':
        chargedays = int( request.POST.get('chargedays') )
        carnum = request.POST.get('carnum')
        print(chargedays)
        print(carnum)
        days = datetime.timedelta(days=chargedays)
        if models.vip_uer.objects.filter(carnum=carnum):
            vip = vip_uer.objects.get(carnum=carnum)
            endtime = vip.endtime + days
            print(vip.endtime)
            models.vip_uer.objects.update(endtime = endtime)
        else:
            begtime = timezone.now()
            endtime = begtime + days
            models.vip_uer.objects.create(carnum=carnum, begintime = begtime ,endtime=endtime)
        context = "充值成功！" + "您的会员截止日期为：" + str(endtime.date())
        return HttpResponse(context)
    else:
        return render(request, 'recharge.html')

def Park_discern(image):
    APP_ID = '自己的APP_ID'
    API_KEY = '自己的API_KEY'
    SECRET_KEY = '自己的SECRET_KEY'
    # 创建客户端对象
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    # 建立连接的超时时间，单位为毫秒
    client.setConnectionTimeoutInMillis(5000)
    # 通过打开的连接传输数据的超时时间，单位为毫秒
    client.setSocketTimeoutInMillis(5000)
    res = client.licensePlate(image)
    return res

def car_in(request):
    if request.method == 'POST':
        # 读取图片
        img = request.FILES.get('car_img')
        if img == None:
            # 没有选择图片，而直接点击检测
            error = '请选择一张图片！'
            return render(request, 'car_in.html', {'error': error})
        else:
            try:
                # 将图片数据存起来
                new_car = models.License_plate.objects.create(car_img=img)

                # 定义读取图片函数
                def get_file_content(filePath):
                    with open(filePath, 'rb') as fp:
                        return fp.read()
                #生成图片地址
                url = './media/' + str(new_car.car_img)
                # 读取图片信息
                image = get_file_content(url)
                # 调用接口识别车牌
                res = Park_discern(image)
                #车牌号
                carnum = res['words_result']['number']
                #车牌颜色
                color = res['words_result']['color']
                try:
                    # 车牌是否识别过
                    is_carnum = models.License_plate.objects.get(car_num=carnum)
                    if is_carnum:
                        #识别过了的直接从数据库读取历史数据并删除当前存储的图片数据和文件
                        new_car.car_img = is_carnum.car_img
                        print(new_car.id )
                        models.License_plate.objects.filter(id=new_car.id ).delete()
                except models.License_plate.DoesNotExist:
                    # 没识别过，则保存车牌和颜色信息
                    new_car.color = color
                    new_car.car_num = carnum
                    new_car.save()
                    # return redirect('carnum_add')
                    print(new_car.car_img)
                return render(request,'car_in.html',{'carport_url':new_car.car_img,'carnum':carnum,'color':color})
            except Exception as e:
                return HttpResponse('识别发生错误！')
    return render(request, 'car_in.html',{'carport_url':'car_imgs/intro.jpg'})

def carin_update(request):
    if request.method == 'POST':
        carnum = request.POST.get('carnum')
        # tz = pytz.timezone('Asia/Shanghai')
        new_intime = timezone.now()
        print(new_intime)
        models.car_record.objects.create(carnum=carnum, intime=new_intime)
        if models.vip_uer.objects.filter(carnum=carnum):
            vip = vip_uer.objects.get(carnum=carnum)
            # now = datetime.now(timezone.utc)
            endtime = vip.endtime
            remain_days = endtime - new_intime
            remain_days = str(remain_days.days)
            context = '会员车辆' + carnum + '欢迎您！'  + '剩余会员天数:' + remain_days
            print(context)
            return HttpResponse(context)
        else:
            return HttpResponse("临时车辆，欢迎入场！")


def car_out(request):
    if request.method == 'POST':
        # 读取图片
        img = request.FILES.get('car_img')
        if img == None:
            # 没有选择图片，而直接点击检测
            error = '请选择一张图片！'
            return render(request, 'car_in.html', {'error': error})
        else:
            try:
                # 将图片数据存起来
                new_car = models.License_plate.objects.create(car_img=img)
                # 定义读取图片函数
                def get_file_content(filePath):
                    with open(filePath, 'rb') as fp:
                        return fp.read()
                #生成图片地址
                url = './media/' + str(new_car.car_img)
                # 读取图片信息
                image = get_file_content(url)
                # 调用接口识别车牌
                res = Park_discern(image)
                #车牌号
                carnum = res['words_result']['number']
                #车牌颜色
                color = res['words_result']['color']
                try:
                    # 车牌是否识别过
                    is_carnum = models.License_plate.objects.get(car_num=carnum)
                    if is_carnum:
                        #识别过了的直接从数据库读取历史数据并删除当前存储的图片数据和文件
                        new_car.car_img = is_carnum.car_img
                        print(new_car.id )
                        models.License_plate.objects.filter(id=new_car.id ).delete()
                except models.License_plate.DoesNotExist:
                    # 没识别过，则保存车牌和颜色信息
                    new_car.color = color
                    new_car.car_num = carnum
                    new_car.save()
                    # return redirect('carnum_add')
                    print(new_car.car_img)
                return render(request,'car_out.html',{'carport_url':new_car.car_img,'carnum':carnum,'color':color})
            except Exception as e:
                return HttpResponse('识别发生错误！')
    return render(request, 'car_out.html',{'carport_url':'car_imgs/intro.jpg'})

def carout_update(request):
    if request.method == 'POST':
        carnum = request.POST.get('carnum')
        new_outtime = timezone.now()
        print(new_outtime)
        new_car_record = car_record.objects.filter(carnum=carnum).order_by('outtime')
        out_car = new_car_record[0]
        out_car.carnum = carnum
        out_car.outtime = new_outtime
        out_car.save()
        if models.vip_uer.objects.filter(carnum=carnum):
            vip = vip_uer.objects.get(carnum=carnum)
            print(vip)
            # now = datetime.now(timezone.utc)
            endtime = vip.endtime
            remain_days = endtime - new_outtime
            remain_days = str(remain_days.days)
            print(remain_days)
            context = '会员车辆' + carnum + '一路顺风！'  + '剩余会员天数:' + remain_days
            print(context)
            return HttpResponse(context)
        else:
            return HttpResponse("临时车辆，一路顺风！")
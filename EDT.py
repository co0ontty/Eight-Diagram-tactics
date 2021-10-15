import configparser
import os
import time
from pick import pick
import random
import string

def get_config(path, file_names):
    cfg_name = file_names[[i for i,x in enumerate(file_names) if x.find('cfg')!=-1][0]]
    cfg_file = os.path.join(path,cfg_name)
    conf = configparser.ConfigParser()
    conf.read(cfg_file)
    sections = conf.sections()
    poc_config = conf.items('poc_config')
    vul_env_config = conf.items('vul_env_config')
    return poc_config, vul_env_config

def change_port(file_name,now_port,new_port):
    print("change_port")
    with open(file_name,'r+') as file:
        original_file = file.read()
        new_file = original_file.replace(str(now_port),str(new_port),1)
        file.seek(0)
        file.truncate()
        file.write(new_file)
def poc_run(poc_config, path, file_names,port_option):
    print("开始攻击,请稍等")
    vul_add = poc_config[2][1]
    if port_option == "no":
        vul_port = poc_config[3][1]
    else:
        vul_port = int(port_option)
    if poc_config[0][1] == "True":
        poc_file = file_names[[i for i,x in enumerate(file_names) if x.find('py')!=-1][0]]
        command = "pocsuite -r {} -u {}:{}".format(os.path.join(path,poc_file),vul_add,vul_port)
        poc_result = os.popen(command).read()
    elif poc_config[0][1] == "False":
        command = poc_config[1][1]
        poc_result = os.popen(command).read()
    if "VerifyInfo : success" in poc_result:
        print("\033[1;31m 攻击成功，防御措施必没生效 \033[0m!")
    else:
        print("\033[1;32m 攻击失败，防御设施可能生效 \033[0m!")


def vul_env_run(vul_env_config, path, file_names,port_option):
    if vul_env_config[0][1] == "True":
        docker_compose_yml = os.path.join(path,file_names[[i for i,x in enumerate(file_names) if x.find('yml')!=-1][0]])
        if port_option != "no":
            change_port(docker_compose_yml,vul_env_config[3][1],int(port_option))
        command = "docker-compose -f {} up -d".format(docker_compose_yml)
        os.system(command)
        if port_option != "no":
            change_port(docker_compose_yml,int(port_option),vul_env_config[3][1])
    elif vul_env_config[0][1] == "False":
        print("\033[1;32m 注意！未使用 docker-compose 部署，请不要使用随机端口选项 \033[0m!")
        command = vul_env_config[1][1]
        os.system(command)
    try:
        print("等待漏洞环境初始化,约{}s (取决于网络速度)".format(int(vul_env_config[2][1])))
        time.sleep(int(vul_env_config[2][1]))
    except:
        print("等待漏洞环境初始化,约{}s (取决于网络速度)".format("10s"))
        time.sleep(10)


def start(path):
    port_option, index = pick(["yes","no"], "是否使用随机端口，部分IPS/IDS仅检测常用端口,随机端口暂时只支持漏洞环境与poc均为框架搭建的情况")
    if port_option == "yes":
        port_option = ''.join(random.sample(string.digits,4))
        print("使用随机端口 {}进行测试".format(port_option))
    file_names = os.listdir(path)
    poc_config, vul_env_config = get_config(path, file_names)
    vul_env_run(vul_env_config, path, file_names,port_option)
    poc_run(poc_config, path, file_names,port_option)

def main():
    env_path = "./env"
    option, index = pick(os.listdir(env_path), "请选择测试用例")
    start(os.path.join(env_path,option))


if __name__ == "__main__":
    main()

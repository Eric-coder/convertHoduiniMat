# coding=utf-8
# _author__ = 'Fan KaiJun'
# Description：

import maya.cmds as cmds
import json
import pymel.core as pm

config = str("C:/Users/Administrator/Desktop/materials_v006/config.json")
out_json = str("C:/Users/Administrator/Desktop/materials_v006/out.json")


def getLongName(name):
    if "|" in name:
        if "." in name:
            root = pm.PyNode(name.split(".")[0])
        else:
            root = pm.PyNode(name)
        ap = root.listRelatives(ap=True)
        root_name = ap[0].longName()
        return root_name + "|" + name


    else:
        return name


def _writeJson(patn_json, write_dict):
    '''write json
            : param patn_json :  such as : "D:/json/dir.json" type :str
            : param patn_json :  such as :{} type:dict
            '''
    with open(patn_json, "w") as films:
        end = json.dumps(write_dict, indent=4)
        films.write(end)


def _readJson(patn_json):
    '''read json
    : param patn_json :  such as : "D:/json/dir.json" type :str
    '''
    with open(patn_json) as file:
        return json.loads(file.read())


def getSgParms(shaders, temp_dict):
    """
    获取与sg相关联的材质的属性值
    :param sg:
    :param temp_dict:
    :return: 字典
    """
    # 获取与sg节点相关联的材质节点

    config_dict = _readJson(config)
    #print config_dict
    shader_name_config = config_dict.keys()[1]
    print shader_name_config
    for attr_name in config_dict[shader_name_config]["parms"].keys():
        print attr_name 
        attr = cmds.getAttr(shaders[0] + attr_name)
        if temp_dict.has_key("parms"):
            temp_dict["parms"][attr_name] = attr
        else:
            temp_dict["parms"] = {}
            temp_dict["parms"][attr_name] = attr
    print "\n"
    temp_dict["Texture"] = {}
    for tex_attr_name in config_dict[shader_name_config]["Texture"].keys():
        #print tex_attr_name
        shading = shaders[0] + tex_attr_name
        #print shading
        if ".displacementShader" not in shading:#判断shading是否包含.displacementShader 不包含执行以下
            Texture = cmds.listConnections(shading, type='file')
            if Texture != None:
                TextureFile = cmds.getAttr("%s.fileTextureName" % Texture[0])
                if temp_dict.has_key("Texture"):
                    temp_dict["Texture"][tex_attr_name] = TextureFile
                else:
                    
                    temp_dict["Texture"][tex_attr_name] = TextureFile
        else:                                #判断shading是否包含.displacementShader 包含执行以下
            shader=shaders[0]+"SG"
            Texture = cmds.listConnections(shader)
            #print Texture
            for i in Texture:
                if 'displacementShader' in i:
                    Text = cmds.listConnections(i,type='file')#判断与'displacementShader'连接的file
                    #print Text
                    TextureFile = cmds.getAttr("%s.fileTextureName" % Text[0])
                    temp_dict["Texture"][".displacementShader"] = TextureFile
        
    print temp_dict["Texture"]
    return temp_dict
    


def outputMaterials():
    """
    输出场景里AiStandard的材质信息
    :return:
    """
    #print 111111
    config_dict = _readJson(config)
    temp_sg = []
    temp_dict = {}

    shapesInSel = cmds.ls(dag=1, o=1, type="mesh")

    for i in range(len(shapesInSel)):
        shadingGrps_list = cmds.listConnections(shapesInSel[i], type='shadingEngine')
        # 去除重复的sg节点
        if shadingGrps_list != None:

            if len(shadingGrps_list) > 1:
                for sg in shadingGrps_list:
                    if sg in shadingGrps_list:
                        shadingGrps_list.remove(sg)
        #print shadingGrps_list
        # 遍历sg节点，获取与其相关联材质的信息
        if shadingGrps_list is not None:
            for sg_name in shadingGrps_list:
                # temp_sg存放已经遍历过了的sg节点防止二次遍历
                if sg_name not in temp_sg:
                    temp_sg.append(sg_name)
                    shader_name_config = config_dict.keys()[1]
                    shaders_node = cmds.ls(cmds.listConnections(sg_name), materials=1)
                    # 判断节点是否是aiStandard node
                    node_type = cmds.nodeType(shaders_node)
                    print shader_name_config
                    if shader_name_config != node_type:
                        temp_dict = getSgParms(shaders_node, temp_dict)
                        try:
                            dict_all = _readJson(out_json)
                        except:
                            dict_all = {}
              
                        if dict_all.has_key("Maya"):
                            dict_all["Maya"][shader_name_config].append(temp_dict)
                        else:
                            dict_all["Maya"] = {}
                            dict_all["Maya"][shader_name_config] = []
                            dict_all["Maya"][shader_name_config].append(temp_dict)
                        # 获取相同材质的所有物体以及面
                        obj_list = cmds.sets(sg_name, int=sg_name)
                        obj_list_name = []
                        obj_list_long_name = []
                        # 获取这些物体的父节点，transform节点，面的除外（pcube.f[1:3]）
                        for obj in obj_list:

                            if "." not in obj:
                                obj_list_name.append(cmds.listRelatives(obj, p=1)[0])
                            else:
                                obj_list_name.append(obj)
                        
                        for shot_name in obj_list_name:
                            if "." in shot_name:
                                if ":" in shot_name and "[" not in shot_name:

                                    name_temp_list_shot = shot_name.split(".")
                                    name_shot = name_temp_list_shot[0].split(":")[1] + "." + name_temp_list_shot[1]
                                    obj_list_long_name.sppend(getLongName(name_shot))
                                else:

                                    obj_list_long_name.append(getLongName(shot_name))
                            else:
                                obj_list_long_name.append(getLongName(shot_name))

                        temp_dict["object_name"] = obj_list_long_name
                        temp_dict["shader_name"] = shaders_node[0]
                        print dict_all
                        _writeJson(out_json, dict_all)

        #print temp_dict
outputMaterials()
#getSgParms(["aiStandardSurface1",'Fangding'], {})

# coding=utf-8

import hou
import json

CONFIG =  str("I:/mayadeskwork/V001/materials_v006/config.json")
INPUT_JSON = str("I:/mayadeskwork/V001/materials_v006/materrials.json")


def import_abc(path):
    """import shape"""
    node = hou.node("obj/")
    abc = node.createNode("alembicarchive", "abc_import")
    abc.setParms({"fileName": path})
    abc.parm("buildHierarchy").pressButton()
    return True


def assign_materials(obj_name, mat_path, merge_input_num, root_name="OperationTable1", obj_merge="pCube1_merge"):
    """
    创建material节点并与物体连接
    :param object_name: 类似 LFDoorWindow or |OperationTable|OperationPlate|FrontCover|LFDoorWindow|
    :param material_name:/mat/aiStandardSurface1
    :param merge_input_num: int类型 与merge的第几个输入点相连
    :param root_name:str类型 OperationTable1
    :param obj_merge:str类型 pCube1_merge
    :return:
    """

    hou.cd("/obj/" + root_name)
    pwd = hou.pwd()
    obj_node = hou.node("/obj/" + root_name + "/" + obj_merge)
    material_node = hou.node("/obj/" + root_name + "/materiall_all")
    merge_node = hou.node("/obj/" + root_name + "/merge_all")
    if obj_node is not None:
        if material_node is None:
            # create materials
            node_shader = pwd.createNode("material", "materiall_all")

            # create meage
            merge = pwd.createNode("merge", "merge_all")

            # connect merge node and material node and obj_node
            merge.setInput(0, obj_node)
            node_shader.setInput(0, merge)

            # set materials node
            material_Parm = node_shader.parm("shop_materialpath1")
            group_Parm = node_shader.parm("group1")

            material_Parm.set(mat_path)
            if "|" in obj_name:
                group_Parm.set(obj_name.replace("|", "_"))
            else:
                group_Parm.set("_" + obj_name)
        else:
            # set materials node

            material_num_parm = material_node.parm("num_materials")
            material_num_parm.set(str(merge_input_num + 1))
            material_Parm = material_node.parm("shop_materialpath" + str(merge_input_num + 1))
            group_Parm = material_node.parm("group" + str(merge_input_num + 1))
            material_Parm.set(mat_path)
            if "|" in obj_name:
                group_Parm.set(obj_name.replace("|", "_"))
            else:
                group_Parm.set("_" + obj_name)
        # Organize the layout under this folder
        layout_node = hou.node("/obj/" + root_name)
        layout_node.layoutChildren()


def assign_face_materials(face_dict, root_name="OperationTable1", sourece_name="object_merge1"):
    """
    指定物体与面的材质 暂时还不能用
    :param face_dict:
    :return:
    """
    obj_name_list = face_dict.keys()
    list_mesh = []

    hou.cd("/obj/" + root_name)

    pwd = hou.pwd()
    merge = pwd.createNode("merge")
    merge_num = 0
    matter_dict = {}
    obj_node = hou.node("/obj/" + root_name + "/" + sourece_name)

    for material_name in face_dict[obj_name].keys():
        if len(face_dict[obj_name][material_name]) > 0:

            list_mesh.append(obj_name)
            # creat group
            group_node = pwd.createNode("group", material_name + "_" + obj_name.replace("|", "_"))

            # creat delete node
            delete_node = pwd.createNode("delete", obj_name.replace("|", "_"))

            # connect delete node and group node and merge and root_obj
            delete_node.setInput(0, obj_node)
            group_node.setInput(0, delete_node)
            merge.setInput(merge_num, group_node)
            merge_num = merge_num + 1

            # set vel
            delete_opara = delete_node.parm("negate")
            delete_group = delete_node.parm("group")
            delete_opara.set(1)
            if "_mesh" in obj_name:
                delete_group.set(obj_name.replace("|", "_"))
            else:
                list_mesh.pop()
                list_name = obj_name.split("|")
                obj_name1 = obj_name + "_" + list_name[-1] + "_mesh"
                list_mesh.append(obj_name1)
                delete_group.set(obj_name1.replace("|", "_"))
                list_mesh.append(obj_name1)

            group_parm = group_node.parm("pattern")
            group_parm.set(" ".join(face_dict[obj_name][material_name]))

            if matter_dict.has_key(material_name):
                matter_dict[material_name].append(group_node.name())
            else:
                matter_dict[material_name] = []
                matter_dict[material_name].append(group_node.name())
        else:
            if matter_dict.has_key(material_name):
                matter_dict[material_name].append(obj_name.replace("|", "_"))
            else:
                matter_dict[material_name] = []
                matter_dict[material_name].append(obj_name.replace("|", "_"))

    # creat delete node other
    delete_other = pwd.createNode("delete")
    # set vel
    delete_opara_ot = delete_other.parm("negate")
    delete_group_ot = delete_other.parm("group")
    delete_opara_ot.set(0)
    delete_group_ot.set(" ".join(list_mesh).replace("|", "_"))
    # connect delete_other and merge and root obj
    merge.setInput(merge_num, delete_other)
    delete_other.setInput(0, obj_node)
    merge_num = merge_num + 1

    # create materials
    node_shader = pwd.createNode("material")
    # connect merge and material
    node_shader.setInput(0, merge)
    # set materials
    material_parm = node_shader.parm("num_materials")
    material_parm.set(len(matter_dict.keys()))
    num = 1

    for mater_name in matter_dict.keys():
        material_Parm = node_shader.parm("shop_materialpath" + str(num))
        group_Parm = node_shader.parm("group" + str(num))
        material_Parm.set("/mat/" + mater_name)
        group_Parm.set(" ".join(matter_dict[mater_name]))
        num = num + 1


def inputMatter(congig, input_json):
    """
    create materials
    :param congig: Material configuration table
    :param input_json :Maya exported material information
    :return:
    """
    with open(congig) as files:
        config_dict = json.loads(files.read())

    with open(input_json) as files1:
        mater_dict = json.loads(files1.read())

    all_materials = mater_dict["Maya"]["aiStandardSurface"]
    matteri_dict = {}

    for i in range(len(all_materials)):

        # if obj_name in all_materials[i]["object_name"]:

        shader = all_materials[i]
        houdini_shader = config_dict["houdini"]

        hou.cd("/mat")
        matpwd = hou.pwd()
        node_shader = matpwd.createNode(houdini_shader, all_materials[i]["shader_name"])

        parms_Tuples = node_shader.parmTuples()
        parms = node_shader.parms()
        # set parm
        parms_dict = all_materials[i]["parms"]
        for parm in parms_dict.keys():
            parm_name = config_dict["aiStandardSurface"]["parms"][parm]
            for tuple_pars in range(len(parms_Tuples)):
                Tuples = parms_Tuples[tuple_pars].name()
                if parm_name == Tuples:

                    pars = parms_dict[parm]
                    types = type(pars)
                    typ = type([1, 2])
                    if types == typ:
                        node_shader.parmTuple(parm_name).set(pars[0])
                    else:
                        node_shader.parm(parm_name).set(pars)

        # set textture

        if all_materials[i].has_key("Texture"):
            texture_dict = all_materials[i]["Texture"]
       #添加displacement
            if ".displacementShader" in texture_dict.keys():
                dis_path=texture_dict[".displacementShader"]
                tex_name=config_dict["aiStandardSurface"]["Texture"][".displacementShader"]
                useDis = tex_name.split('_')[0]
                useDis += '_enable'
                node_shader.parm(useDis).set(True)
                node_shader.parm(tex_name).set(dis_path)
           ####  
           
            for text in parms_dict.keys():
                
                if texture_dict.has_key(text):
                    file_path = texture_dict[text]
                    text_name = config_dict["aiStandardSurface"]["Texture"][text]
                    if file_path != '':
                        useTex = text_name.split('_')[0]
                        useTex += '_useTexture'
                        node_shader.parm(useTex).set(True)
                        node_shader.parm(text_name).set(file_path)
                else:
                    pass


inputMatter(CONFIG, INPUT_JSON)
# assign_materials("pCube1", "/mat/aiStandardSurface1", 2, "OperationTable1", "pCube1_merge")
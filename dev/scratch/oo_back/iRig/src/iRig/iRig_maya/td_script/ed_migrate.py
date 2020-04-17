#migrate deformers script

#Created by Eldon Derksen
#help and assisting code by Alison Chan and Alex Gaidachev

import maya.cmds as cmds
import tool_panel
toolpanel = tool_panel.ToolWindow()
toolpanel.dock_ui()
import deform_utils
reload(deform_utils)
from functools import partial

#start_time = cmds.timerX()

# get asset type
def get_asset_type():
    type = ['Character', 'Prop', 'Set', 'Vehicle']
 
    asset = []
    for i in type:
        if cmds.ls(i):
            asset.append(i)
        
    if len(asset) == 1:
        asset = asset[0]

    return asset

# get node history by type function
def get_nodes_by_type(typ='', obj_name=''):    
    nodes = []
    listHis = cmds.listHistory(obj_name,  il=2, pdo=True)
    if listHis is not None:
        for node in listHis:
            if cmds.nodeType(node) == typ:
                nodes.append(node)
        nodes.reverse()
    return nodes

#get vertices and memebership check
def check_membership(vert_check, def_check):
    
    list_vtx = cmds.ls(vert_check + '.vtx[*]')
    set = deform_utils.util_find_deformer_set(deformer=def_check)
    mem_check = cmds.sets( list_vtx, im=set )
    return mem_check, list_vtx

  
#remove non-membership verts from new set
def remove_verts(rem_obj, new_geo_obj, def_obj, new_def_obj):
    
    check_mem = check_membership(rem_obj, def_obj)
    if not check_mem[0]:
        print(rem_obj + " has removed verts from " + def_obj + " deformer.")
        cmds.select(check_mem[1], r=True)
        set = deform_utils.util_find_deformer_set(deformer=def_obj)
        set_vtx = cmds.sets(set, q=True)
        cmds.select(set_vtx, d=True)
        removed_vtx = cmds.ls(sl=True)
        remove_vtx = []
        for vtx in removed_vtx:
            remove_vtx.append(vtx.replace(rem_obj, new_geo_obj))
        cmds.select(new_geo_obj)
        new_def = new_def_obj
        new_set = deform_utils.util_find_deformer_set(deformer=new_def)  
        for vtx in remove_vtx:
            cmds.sets(vtx, remove=new_set)
    return check_mem[0], check_mem[1]


#get deformer weights per vert
def get_set_weights(obj_name, new_geo_name, def_name):

    vtx_list = cmds.ls(obj_name, fl=True)    
    vtx_weights = {}
    for vtx in vtx_list:
        val = cmds.percent(def_name, vtx, v=True, q=True)
        if val[0] != 0 and val[0] != 1: 
            vtx_split = vtx.split('.')
            vtx = new_geo_name + '.' + vtx_split[1]
            vtx_weights[vtx] = val[0]
    
    for vtx, val in vtx_weights.items():
        #print(vtx, val)
        cmds.percent(def_name, vtx, v=val)

#check the constraint type
def constraint_type(children_type='', children_list=['']):
    target = []
    for child in children_list:
        if cmds.objectType(child, isType=children_type):
            temp = cmds.listConnections(child + '.target')  
            if child in temp: 
                temp.remove(child)
            temp = list(dict.fromkeys(temp))
            target.append(temp[0])
    return target

def migrate_deformers(type='body', *args):
    #select all old geo that didn't properly swap over from Import to Reference
    sel = cmds.ls(sl=True)
    #print(len(sel))
    
    ref_check = []
    for each in sel:
        if ":" in each:
            ref_check.append(each)
            
    if len(ref_check) > 0:        
        cmds.warning('Please only select source geometry, which should be unreferenced.')
    else:
    
        for old_geo in sel:
            
            cmds.select(old_geo, r=True)
            if type == 'face':
                split = old_geo.split(str(1))
                new_geo = cmds.ls("*Face*" + "*:" + split[0])
            else:
                new_geo = cmds.ls("*:" + old_geo)
            if len(new_geo) > 1:
                for each in new_geo:
                    if "Face" in each:
                        new_geo.remove(each)
                if len(new_geo) > 1: 
                    cmds.warning("Multiple source meshes found, please be sure there is only one source mesh.")
            
            if len(new_geo) == 1:
                new_geo = new_geo[0]
                
                obj = cmds.rename(old_geo, old_geo +  "_OLD")
                
                if cmds.objExists(new_geo):
                
                    #get nodes
                    skin = get_nodes_by_type(typ='skinCluster', obj_name=obj)
                    bsh = get_nodes_by_type(typ='blendShape', obj_name=obj)
                    nonlin = get_nodes_by_type(typ='nonLinear', obj_name=obj)
                    lat = get_nodes_by_type(typ='ffd', obj_name=obj)
                    wire_def = get_nodes_by_type(typ='wire', obj_name=obj)
                    cluster_def = get_nodes_by_type(typ='cluster', obj_name=obj)
                    
                    historyOrder = cmds.listHistory(obj, il=2, pdo=True)
                    if historyOrder is not None:
                        historyOrder.reverse()
                        for input in historyOrder:
                            
                            if type == 'face':
                                cmds.namespace(set=new_geo.split(":")[0])
                                    
                            #bsh
                            if len(bsh) > 0 and input in bsh:
                                bsh_source = cmds.listConnections(input + '.inputTarget')
                                if input == old_geo + '_BSH':
                                    input = cmds.rename(input, old_geo + '_BSH_OLD')
                                try:
                                    bsh_new = cmds.blendShape(bsh_source, new_geo, n=(old_geo + '_BSH'))
                                    cmds.setAttr( str(bsh_new[0] + '.' + bsh_source[0]), 1)
                                    has_weights = remove_verts(obj, new_geo, input, bsh_new[0])
                                    if not has_weights[0]:
                                        get_set_weights(has_weights[1], new_geo, input)
                                except:
                                    print(new_geo + ' - Could not blendshape source to this target. Shapes do not match.')

                                                 
                            #skinCluster
                            if len(skin) > 0 and input in skin:
                                if type == 'body':
                                    skin_old = get_nodes_by_type('skinCluster', obj_name=obj)[0]
                                    skin_inf = cmds.skinCluster(skin_old, q=True, inf=True)
                                    skin_new = cmds.skinCluster(skin_inf, new_geo, tsb=True, n=old_geo + '_skinCluster')[0]
                                    cmds.copySkinWeights(ss=skin_old, ds=skin_new, noMirror=True, surfaceAssociation="closestPoint", ia="oneToOne", normalize=True)
                                    remove_verts(obj, new_geo, input, skin_new)
                
                            #lattice
                            if len(lat) > 0 and input in lat:
                                cmds.deformer( input, e=True, g=new_geo )
                                remove_verts(obj, new_geo, input, input) 
                                               
                            #non linear
                            if len(nonlin) > 0 and input in nonlin:
                                cmds.deformer( input, e=True, g=new_geo )   
                                has_weights = remove_verts(obj, new_geo, input, input)   
                                if not has_weights[0]:
                                    get_set_weights(has_weights[1], new_geo, input)
            
                            #wire
                            if len(wire_def) > 0 and input in wire_def:
                                cmds.deformer( input, e=True, g=new_geo )
                                has_weights = remove_verts(obj, new_geo, input, input)   
                                if not has_weights[0]:
                                    get_set_weights(has_weights[1], new_geo, input)                                                                     
        
                            #cluster
                            if len(cluster_def) > 0 and input in cluster_def:
                                cmds.deformer( input, e=True, g=new_geo )
                                has_weights = remove_verts(obj, new_geo, input, input)   
                                if not has_weights[0]:
                                    get_set_weights(has_weights[1], new_geo, input)   
                                    
                            if type == 'face':                                    
                                cmds.namespace(set=':')
                        
                    #shaders                      
                    shapesInSel =  cmds.ls(obj, dag=1,o=1,s=1)
                    shadingGrps = cmds.listConnections(shapesInSel,type='shadingEngine')
                    shaders = cmds.ls(cmds.listConnections(shadingGrps),materials=1)
                    shaders = list(dict.fromkeys(shaders))
                    if len(shaders) > 1:
                        if 'lambert1' in shaders: 
                            shaders.remove('lambert1')
                                      
                    if len(shaders) == 1:
                        if(shaders[0] != 'lambert1'): 
                            shader_group = cmds.listConnections(shaders[0],type='shadingEngine')[0]   
                            cmds.sets(new_geo, e=True, forceElement= shader_group)                
                            #cmds.sets(new_geo, e=True, forceElement= shaders[0] + 'SG')
                        else:                       
                            cmds.sets(new_geo, e=True, forceElement= 'initialShadingGroup') 
                        
                    #add vert check for len(shaders) > 1
                    old_vert = cmds.polyEvaluate(obj, f=True)
                    new_vert = cmds.polyEvaluate(new_geo, f=True)            
                        
                    if len(shaders) > 1 and old_vert == new_vert:
                        
                        for shader in shaders:
                            shader_group = cmds.listConnections(shader,type='shadingEngine')[0]  
                            assigned_to_shader = cmds.sets(shader_group, q=True)
                            
                            #namespace to shape nodes
                            ns = new_geo.rpartition(':')[0]                                                                                  
                            shape_list = cmds.ls(new_geo, dag=1,o=1,s=1)
                            for each in shape_list:
                                if not ":" in each:
                                    cmds.rename(each, ns+ ':' + each)
                            
                            #remove non '_OLD' geo
                            shader_list = []
                            for each in assigned_to_shader:
                                if (each.find('_OLD') > 0) and (each.find(old_geo) != -1):
                                    new_name = each.replace("_OLD", "")
                                    new_name = '*:' + new_name
                                    shader_list.append(new_name)
                                    
                            if(shader != 'lambert1'):
                                cmds.sets(shader_list, e=True, forceElement= shader_group)   
                            else:
                                cmds.sets(shader_list, e=True, forceElement= 'initialShadingGroup') 
    
                    #vis toggle on geo check  
                    vis_check = cmds.listConnections(obj + '.visibility', c=True, p=True)
                    if vis_check is not None:
                        cmds.connectAttr(vis_check[1], new_geo + '.visibility')
                      
                    #geo constraint check            
                    children = cmds.listConnections(obj, s=True, d=False) 
                    if children is not None:
                        children = list(dict.fromkeys(children))
                    
                        parent_cns = constraint_type(children_type='parentConstraint', children_list=children)
                        scale_cns = constraint_type(children_type='scaleConstraint', children_list=children)
                        point_cns = constraint_type(children_type='pointConstraint', children_list=children)
                        orient_cns = constraint_type(children_type='orientConstraint', children_list=children)
                        aim_cns = constraint_type(children_type='aimConstraint', children_list=children)
                        
                        if len(parent_cns) > 0:
                            cmds.parentConstraint(parent_cns, new_geo, mo=True)
                        if len(scale_cns) > 0:
                            cmds.scaleConstraint(scale_cns, new_geo, mo=True)    
                        if len(point_cns) > 0:
                            cmds.pointConstraint(point_cns, new_geo, mo=True)
                        if len(orient_cns) > 0:
                            cmds.pointConstraint(orient_cns, new_geo, mo=True)
                        if len(aim_cns) > 0:
                            cmds.aimConstraint(aim_cns, new_geo, mo=True)
         
                    #reparent old and new geo
                    asset_type = get_asset_type()
                    parentNode = cmds.listRelatives(obj, p=True)
                    if parentNode:
                        cmds.parent(obj, world=True)
                        if type == 'body':
                            if asset_type == 'Character' or asset_type == 'Prop':
                                cmds.parent(new_geo, parentNode)
                            
                    #cleanup for face section
                    if type == 'face':
                        outputs = cmds.listHistory(obj, il=2, future=True, pdo=True)
                        for i in outputs:
                            if cmds.nodeType(i) == 'blendShape':
                                cmds.delete(i)
                        cmds.delete(obj)
                        
                        
                                            
                    print (obj +' - is done!')           
    
    print('All selected geo has been migrated!')
    #total_time = cmds.timerX(startTime=start_time)
    #print ("Total Time: ", total_time)

def migrate_window():
    if cmds.window("migrateWin", ex=True) == True:
        cmds.deleteUI("migrateWin")

    cmds.window("migrateWin", t="ED Migrate Tool")
    cmds.columnLayout(adj=True, width=300)
    cmds.button("Migrate - Default (Body)", l="Migrate - Default (Body)", h=50, c=partial(migrate_deformers, 'body'))
    cmds.button("Migrate - SMO (Face)", l="Migrate - SMO (Face)", h=50, c=partial(migrate_deformers, 'face'))
    cmds.showWindow("migrateWin")


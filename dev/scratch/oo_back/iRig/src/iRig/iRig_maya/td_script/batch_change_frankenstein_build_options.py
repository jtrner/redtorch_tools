# Batch Change Orient Options
import cPickle as pickle

# make array with info to change
attrib_list = [(u'L_Arm_Info',
 [('orient_joints_up_axis', u'ydown'),
  ('do_orient_joints', True),
  ('orient_joints', u'yzx')]),
(u'L_Clavicle_Info',
 [('orient_joints_up_axis', u'zup'),
  ('do_orient_joints', False),
  ('orient_joints', u'yzx')]),
(u'R_Arm_Info',
 [('orient_joints_up_axis', u'ydown'),
  ('do_orient_joints', False),
  ('orient_joints', u'yzx')]),
(u'R_Clavicle_Info',
 [('orient_joints_up_axis', u'zup'),
  ('do_orient_joints', False),
  ('orient_joints', u'yzx')])]

for info in attrib_list:
    # iterate through array
    attrib = str(info[0])+".build_data"
    for key in info[1]:
        keyToModify = key[0]
        newValue = key[1]

        # unlock data
        cmds.setAttr(attrib, l=False)

        # get data from scene
        data_as_str = cmds.getAttr(attrib)  # get serialized string data
        data_eval = pickle.loads(str(data_as_str))  # convert serialized str to dictionary

        # setting data
        data_eval[keyToModify] = newValue  # set dictionary to new value

        # storing data back into scene
        build_data_pickle = pickle.dumps(data_eval)  # converts updated dictionary back into a string to store
        cmds.setAttr(attrib, build_data_pickle, type='string')  # stores the serialzed string back into the rig

        # Making sure it worked
        data_as_str = cmds.getAttr(attrib)  # get serialized string data
        data_eval = pickle.loads(str(data_as_str))  # convert serialized str to dictionary
        print(attrib+' '+keyToModify+' '+str(data_eval[keyToModify]))  # print value  # print value
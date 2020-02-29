oldDir = "//server/bfd/"
newDir = "M:/"

for n in nuke.allNodes():
    if n.Class() == "Read" or n.Class() == "ReadGeo" or n.Class() == "ReadGeo2" or n.Class() == "Axis2":
        f = n.knob( "file" )
        filename =  f.getValue()
        f.setValue( filename.replace(oldDir, newDir) )

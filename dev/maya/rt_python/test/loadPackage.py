import pkgutil


def importPackage(package):
    prefix = package.__name__ + "."
    for importer, modname, ispkg in pkgutil.iter_modules(package.__path__, prefix):
        module = __import__(modname, fromlist='dummy')
        print "Imported: ", module
        
        if ispkg:
            importPackage(module)            
     
import main_pack
importPackage(main_pack)

a = getattr(eval('main_pack.lib.displayLib'), 'SUB_COLOR')



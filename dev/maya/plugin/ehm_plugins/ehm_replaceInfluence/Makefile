MAYA = 2018

include ../../buildconfig

BUILD_DIR ?= ../../$(MAYA)/$(BUILD_PLATARCHOS)/plugins/build


##################################
# Platform specific build settings
##################################
OUTPUT_PLUGIN = replaceInfluence.so

C++           = g++

CFLAGS        = -DLINUX -D_BOOL -DREQUIRE_IOSTREAM -DBits64_ -DLINUX_64 -fPIC -O3
C++FLAGS      = $(CFLAGS) -fopenmp -Wno-deprecated -fno-gnu-keywords

LD            = $(C++) $(NO_TRANS_LINK) $(C++FLAGS) -Wl,-Bsymbolic -shared

INCLUDES      = -I. -I$(MAYA_LOCATION)/include
LIBS          = -L$(MAYA_LOCATION)/lib -liomp5

.cpp.o:
    $(C++) -c $(INCLUDES) $(C++FLAGS) $<

plugins: $(BUILD_DIR)/$(OUTPUT_PLUGIN)

clean:
    -rm -f *.o

##################
# Specific Rules #
##################

OBJECTS = ./src/pluginMain.o \
          ./src/replaceInfluence.o \


$(BUILD_DIR)/$(OUTPUT_PLUGIN): $(OBJECTS)
    @ echo ------------------------------------------------------------
    @ echo Building $(OUTPUT_PLUGIN) for Maya $(MAYA_VER)
    @ echo To: $(BUILD_DIR)/$(OUTPUT_PLUGIN)
    @ echo At: $(LOCATION)
    @ echo ------------------------------------------------------------
    -mkdir -p $(dir $@)
    -rm -f $@
    $(LD) -o $(BUILD_DIR)/$(OUTPUT_PLUGIN) ./*.o $(LIBS) -lOpenMaya -lFoundation -lOpenMayaUI -lOpenMayaAnim -lOpenMayaFX



{"url": "https://docs.google.com/open?id=17dgh9n8Shhx3KWdjtosM0TrhV52ieqBJezlDv7aUyXg", "doc_id": "17dgh9n8Shhx3KWdjtosM0TrhV52ieqBJezlDv7aUyXg", "email": "contact.ehm@gmail.com"}
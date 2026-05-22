class GUI.OSD_Components.Geom
{
   static var __sensorWidth;
   static var __sensorHeight;
   static var __recordWidth;
   static var __recordHeight;
   static var __panelHeight;
   static var __sensorX;
   static var __sensorY;
   static var __evfWidth = 1280;
   static var __evfHeight = 848;
   static var __safeWidth = GUI.OSD_Components.Geom.__recordWidth;
   static var __safeHeight = GUI.OSD_Components.Geom.__recordHeight;
   static var sensorMode = [{mode:"4k_35mm",__sensorWidth:1280,__sensorHeight:720,__recordWidth:1170,__recordHeight:658,__panelHeight:64},{mode:"4k2:1",__sensorWidth:1280,__sensorHeight:720,__recordWidth:1170,__recordHeight:585,__panelHeight:64},{mode:"2k_35mm",__sensorWidth:1280,__sensorHeight:720,__recordWidth:1170,__recordHeight:658,__panelHeight:64},{mode:"1080_35mm",__sensorWidth:1280,__sensorHeight:720,__recordWidth:1097,__recordHeight:617,__panelHeight:64},{mode:"720_35mm",__sensorWidth:1175,__sensorHeight:672,__recordWidth:1024,__recordHeight:576,__panelHeight:64},{mode:"2k_16mm",__sensorWidth:1280,__sensorHeight:720,__recordWidth:1170,__recordHeight:658,__panelHeight:64},{mode:"1080_16mm",__sensorWidth:1280,__sensorHeight:720,__recordWidth:1097,__recordHeight:617,__panelHeight:64},{mode:"720_16mm",__sensorWidth:1175,__sensorHeight:672,__recordWidth:1024,__recordHeight:576,__panelHeight:64}];
   function Geom(mode)
   {
      GUI.OSD_Components.Geom.Configure(mode);
   }
   static function Configure(mode)
   {
      var _loc1_ = 0;
      while(_loc1_ < GUI.OSD_Components.Geom.sensorMode.length)
      {
         if(GUI.OSD_Components.Geom.sensorMode[_loc1_].mode == mode)
         {
            break;
         }
         _loc1_ = _loc1_ + 1;
      }
      if(_loc1_ == GUI.OSD_Components.Geom.sensorMode.length)
      {
         _loc1_ = 0;
      }
      GUI.OSD_Components.Geom.__sensorWidth = GUI.OSD_Components.Geom.sensorMode[_loc1_].__sensorWidth;
      GUI.OSD_Components.Geom.__sensorHeight = GUI.OSD_Components.Geom.sensorMode[_loc1_].__sensorHeight;
      GUI.OSD_Components.Geom.__recordWidth = GUI.OSD_Components.Geom.sensorMode[_loc1_].__recordWidth;
      GUI.OSD_Components.Geom.__recordHeight = GUI.OSD_Components.Geom.sensorMode[_loc1_].__recordHeight;
      GUI.OSD_Components.Geom.__panelHeight = GUI.OSD_Components.Geom.sensorMode[_loc1_].__panelHeight;
      GUI.OSD_Components.Geom.__safeWidth = GUI.OSD_Components.Geom.__recordWidth;
      GUI.OSD_Components.Geom.__safeHeight = GUI.OSD_Components.Geom.__recordHeight;
      GUI.OSD_Components.Geom.__sensorX = (GUI.OSD_Components.Geom.__evfWidth - GUI.OSD_Components.Geom.__sensorWidth) / 2;
      GUI.OSD_Components.Geom.__sensorY = (GUI.OSD_Components.Geom.__evfHeight - GUI.OSD_Components.Geom.__sensorHeight) / 2;
   }
   static function getEvfWidth()
   {
      return GUI.OSD_Components.Geom.__evfWidth;
   }
   static function getEvfHeight()
   {
      return GUI.OSD_Components.Geom.__evfHeight;
   }
   static function getSensorX()
   {
      return GUI.OSD_Components.Geom.__sensorX;
   }
   static function getSensorY()
   {
      return GUI.OSD_Components.Geom.__sensorY;
   }
   static function getSensorWidth()
   {
      return GUI.OSD_Components.Geom.__sensorWidth;
   }
   static function getSensorHeight()
   {
      return GUI.OSD_Components.Geom.__sensorHeight;
   }
   static function getRecordWidth()
   {
      return GUI.OSD_Components.Geom.__recordWidth;
   }
   static function getRecordHeight()
   {
      return GUI.OSD_Components.Geom.__recordHeight;
   }
   static function getSafeWidth()
   {
      return GUI.OSD_Components.Geom.__safeWidth;
   }
   static function getSafeHeight()
   {
      return GUI.OSD_Components.Geom.__safeHeight;
   }
   static function getPanelWidth()
   {
      return GUI.OSD_Components.Geom.__evfWidth;
   }
   static function getPanelHeight()
   {
      return GUI.OSD_Components.Geom.__panelHeight;
   }
   static function setSafeWidth(width)
   {
      GUI.OSD_Components.Geom.__safeWidth = width;
   }
   static function setSafeHeight(height)
   {
      GUI.OSD_Components.Geom.__safeHeight = height;
   }
}

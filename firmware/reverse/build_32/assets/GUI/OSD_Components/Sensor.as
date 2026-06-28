class GUI.OSD_Components.Sensor extends MovieClip
{
   var __gpdb;
   var __infoBox;
   var __lookAround;
   var __mc;
   var __mcFilm;
   var __warningBoxMC;
   var __zoomActive;
   var __zoomPosX;
   var __zoomPosY;
   var __zoomResolution;
   static var __manager;
   var __evfWidth = 1280;
   var __evfHeight = 848;
   function Sensor(parent, depth)
   {
      super();
      _global.VxDebug("...........................................................................CTOR Sensor()");
      this.__gpdb = _global.gpdb;
      this.__mc = this;
      GUI.OSD_Components.Sensor.__manager = this;
      this.InitSensorWidgets();
      this.AddCallbacks();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.Sensor.__manager === undefined)
      {
         throw new Error("Sensor::GetManager() Called before created");
      }
      return GUI.OSD_Components.Sensor.__manager;
   }
   function InitSensorWidgets()
   {
      this.__mcFilm = this.__mc.mcFilm;
      this.__mcFilm._visible = true;
      this.__lookAround = new GUI.OSD_Components.LookAround(this.__mc,this.__mc.getNextHighestDepth());
      new GUI.OSD_Components.Reticle(this.__mc,this.__mc.getNextHighestDepth());
      new GUI.OSD_Components.Frame(this.__mc,this.__mc.getNextHighestDepth());
      this.SyncGeomWithPDB();
      this.__mc.attachMovie("WarningPaneMC","mcWarning",this.__mc.getNextHighestDepth());
      this.__warningBoxMC = this.__mc.mcWarning;
      this.__mc.createTextField("infoBox",this.__mc.getNextHighestDepth(),0,680,1280,100);
      this.__infoBox = this.__mc.infoBox;
      this.__infoBox.multiline = false;
      this.__infoBox.wordWrap = false;
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE",_loc2_);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.MAGNIFICATION.POSITION_X",_loc2_);
      this.__gpdb.addCallback("IMAGE_ANALYSIS.MAGNIFICATION.POSITION_Y",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.RESOLUTION",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "IMAGE_ANALYSIS.MAGNIFICATION.ENABLE":
         case "IMAGE_ANALYSIS.MAGNIFICATION.POSITION_X":
         case "IMAGE_ANALYSIS.MAGNIFICATION.POSITION_Y":
         case "PROJECT.MODE_MATRIX.RESOLUTION":
            this.SyncGeomWithPDB();
         default:
            return;
      }
   }
   function SetZoomPosition(x, y)
   {
      var _loc4_ = x != this.__zoomPosX || y != this.__zoomPosY;
      if(_loc4_)
      {
         this.SetGeometry(this.__zoomActive,this.__zoomResolution,x,y);
      }
      this.__gpdb.paramSet("IMAGE_ANALYSIS.MAGNIFICATION.POSITION_X",x.toString());
      this.__gpdb.paramSet("IMAGE_ANALYSIS.MAGNIFICATION.POSITION_Y",y.toString());
   }
   function SetGeometry(zoomActive, resolution, x, y)
   {
      var _loc3_ = 100;
      var _loc15_ = 175;
      var _loc14_ = 175;
      var _loc6_ = 131;
      var _loc8_ = 117;
      var _loc10_ = 200;
      var _loc7_ = 200;
      var _loc17_ = 150;
      var _loc9_ = 160;
      var _loc16_ = 160;
      var _loc12_ = 120;
      var _loc11_ = 107;
      var _loc13_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc4_ = this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.MAG1TO1");
      if(_loc13_)
      {
         switch(resolution)
         {
            case "4.5K":
            case "4KOS":
               _loc3_ = _loc9_;
               break;
            case "4K":
            case "4K2:1":
            case "4KHS":
            case "4K1.2:1":
            case "4KHD":
            case "4K40":
               _loc3_ = _loc16_;
               break;
            case "3K":
            case "3K2:1":
            case "3K1.2:1":
               _loc3_ = _loc12_;
               break;
            case "2K":
            case "2K2:1":
            case "2K1.2:1":
            case "RGB1080P":
            case "RGB720P":
               _loc3_ = _loc11_;
               break;
            default:
               _global.VxError("Sensor::ScaleSensorObjects() Unhandled playback resolution \'" + resolution + "\'");
         }
      }
      else
      {
         switch(resolution)
         {
            case "4.5K":
            case "4KOS":
               _loc3_ = _loc15_;
               break;
            case "4K":
            case "4K2:1":
            case "4KHS":
            case "4K1.2:1":
            case "4KHD":
            case "4K40":
            case "RGB1080P":
            case "RGB720P":
               _loc3_ = !_loc4_ ? _loc14_ : _loc10_;
               break;
            case "3K":
            case "3K2:1":
            case "3K1.2:1":
               _loc3_ = !_loc4_ ? _loc6_ : _loc7_;
               break;
            case "2K":
            case "2K2:1":
            case "2K1.2:1":
               _loc3_ = !_loc4_ ? _loc8_ : _loc17_;
               break;
            default:
               _global.VxError("Sensor::ScaleSensorObjects() Unhandled record resolution \'" + resolution + "\'");
         }
      }
      this.__mc._x = 0;
      this.__mc._y = 0;
      this.__mc._y += 64;
      this.__mc._xscale = 100;
      this.__mc._yscale = 100;
      this.__zoomPosX = x;
      this.__zoomPosY = y;
      this.__zoomResolution = resolution;
      this.__zoomActive = zoomActive;
   }
   function SyncGeomWithPDB()
   {
      var _loc2_ = this.__gpdb.paramGetBoolean("IMAGE_ANALYSIS.MAGNIFICATION.ENABLE");
      var _loc5_ = this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION");
      var _loc4_ = this.__gpdb.paramGetNumber("IMAGE_ANALYSIS.MAGNIFICATION.POSITION_X");
      var _loc3_ = this.__gpdb.paramGetNumber("IMAGE_ANALYSIS.MAGNIFICATION.POSITION_Y");
      var _loc6_ = _loc2_ != this.__zoomActive || _loc4_ != this.__zoomPosX || _loc3_ != this.__zoomPosY || _loc5_ != this.__zoomResolution;
      if(_loc6_)
      {
         this.SetGeometry(_loc2_,_loc5_,_loc4_,_loc3_);
      }
   }
   function UpdateGeom()
   {
      this.__mc._x = GUI.OSD_Components.Geom.getSensorX();
      this.__mc._y = GUI.OSD_Components.Geom.getSensorY();
      this.__mcFilm._xscale = 100 * (GUI.OSD_Components.Geom.getSensorWidth() / 1280);
      this.__mcFilm._yscale = 100 * (GUI.OSD_Components.Geom.getSensorHeight() / 720);
      this.__lookAround.UpdateGeom();
   }
   function LoadPlot(filename)
   {
      var _loc2_ = "/roFs/NAB/" + filename;
      this.__mcFilm.loadMovie(_loc2_);
      this.__mcFilm._visible = true;
   }
   function HidePlot()
   {
      this.__mcFilm._visible = false;
   }
   function alpha(value)
   {
      this.__mcFilm._alpha = value;
   }
   function showWarning(text)
   {
      this.__warningBoxMC.Show(text);
   }
   function hideWarning()
   {
      this.__warningBoxMC.Hide();
   }
   function showInfo(text)
   {
      this.__mcFilm._alpha = 30;
      this.__infoBox._visible = true;
      this.__infoBox.text = text;
      var _loc2_ = new TextFormat();
      _loc2_.color = 14737632;
      _loc2_.size = 24;
      _loc2_.font = "arial";
      _loc2_.align = "center";
      this.__infoBox.setTextFormat(_loc2_);
   }
   function hideInfo()
   {
      this.__mcFilm._alpha = 100;
      this.__infoBox._visible = false;
   }
}

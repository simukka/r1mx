class GUI.OSD_Components.Widget_DigMag extends MovieClip
{
   var __dmCompression;
   var __dmEncoding;
   var __dmFrameRate;
   var __dmMedia;
   var __dmMounted;
   var __dmResolution;
   var __gpdb;
   var __mediaMgr;
   var __symFPS;
   var __textField_encoding;
   var __textField_format;
   var __textField_fps;
   var __textField_media1;
   var __textField_media2;
   var __textField_media3;
   var __textField_state1;
   var __textField_state2;
   var __textField_state3;
   var __notPresentDRIVE0 = false;
   var __notPresentDRIVE1 = false;
   var FRAME_MEDIA_PRESENT = 1;
   var FRAME_NO_MEDIA = 2;
   function Widget_DigMag()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.__mediaMgr = GUI.OSD_Components.MediaManager.GetManager();
      this.__symFPS._visible = false;
      this.__notPresentDRIVE0 = true;
      this.__notPresentDRIVE1 = true;
      this.__dmCompression = this.__gpdb.paramGet("MEDIA.DIGMAG.PROJECT.COMPRESSION");
      this.__dmEncoding = this.__gpdb.paramGet("MEDIA.DIGMAG.PROJECT.ENCODING");
      this.__dmResolution = this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION");
      this.__dmFrameRate = this.__gpdb.paramGet("MEDIA.DIGMAG.PROJECT.FRAME_RATE");
      this.UpdateDigmagVisual();
      this.PaintProjectInfo();
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.RUN_STATE",_loc2_);
      this.__gpdb.addCallback("PROJECT.PRIMARY_MEDIA",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.SELECTION_POLICY",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.DRIVE0.GUI_STATE",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.DRIVE1.GUI_STATE",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.ACTIVEDRIVE",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.TYPE",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.PROJECT.COMPRESSION",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.PROJECT.ENCODING",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.PROJECT.FRAME_RATE",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.PROJECT_SETTINGS_RECORDABLE",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.COMPRESSION",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.ENCODING",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.RESOLUTION",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.FRAME_RATE",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.QUALITY",_loc2_);
   }
   function HandleDigmagState(name, value)
   {
      var _loc3_ = name != "MEDIA.DIGMAG.DRIVE0.GUI_STATE" ? "DRIVE1" : "DRIVE0";
      switch(value)
      {
         case "NOTPRESENT":
            this["__notPresent" + _loc3_] = true;
            break;
         case "MOUNTED":
         case "UNCONFIGURED":
         case "INCOMPATIBLE":
            this.HandleInsertionState(_loc3_);
            break;
         case "NOTMOUNTED":
         case "UNMOUNTED":
         case "EXPORTED":
            break;
         default:
            _global.VxError("Widget_DigMag::UpdateDigmagVisual() Unknown drive state: " + driveState);
      }
      if("DigMag" == this.__gpdb.paramGet("PROJECT.PRIMARY_MEDIA"))
      {
         this.UpdateDigmagVisual();
      }
   }
   function HandleInsertionState(targettedDrive)
   {
      var _loc2_ = "Unknown" == this.__gpdb.paramGet("MEDIA.DIGMAG.TYPE");
      var _loc3_;
      if(_loc2_ && this["__notPresent" + targettedDrive])
      {
         _loc3_ = this.__gpdb.paramGetBoolean("MEDIA.DIGMAG.DRIVE0.FORMAT_REQUEST") || this.__gpdb.paramGetBoolean("MEDIA.DIGMAG.DRIVE1.FORMAT_REQUEST");
         if(!_loc3_)
         {
            this.__gpdb.paramSet("SYSTEM.ERROR.GENERAL","MEDIA_TYPE_UNKNOWN");
            this.UpdateDigmagVisual();
         }
      }
      this["__notPresent" + targettedDrive] = false;
   }
   function RecordingQualityString()
   {
      var _loc3_ = this.__gpdb.paramGet("PROJECT.MODE_MATRIX.QUALITY");
      var _loc2_;
      switch(_loc3_)
      {
         case "REDCODE42":
            _loc2_ = "RC42";
            break;
         case "REDCODE36":
            _loc2_ = "RC36";
            break;
         case "REDCODE28":
         default:
            _loc2_ = "RC28";
      }
      return _loc2_;
   }
   function UpdateDigmagVisual()
   {
      var _loc6_ = this.__gpdb.paramGet("PROJECT.PRIMARY_MEDIA");
      this.__dmMedia = _loc6_;
      this.__dmMounted = false;
      var _loc5_;
      var _loc9_;
      var _loc8_;
      var _loc4_;
      var _loc7_;
      switch(_loc6_)
      {
         case "RAW Port":
            this.__dmMounted = true;
            this.__textField_media1.text = "RAW";
            this.__textField_media2.text = "";
            this.__textField_media3.text = "Port";
            break;
         case "HD-SDI":
            this.__dmMounted = true;
            this.__textField_media1.text = "";
            this.__textField_media2.text = "HD-SDI";
            this.__textField_media3.text = "";
            break;
         case "DigMag":
            this.gotoAndStop(this.FRAME_NO_MEDIA);
            if("NOTPRESENT" == this.__gpdb.paramGet("MEDIA.DIGMAG.DRIVE0.GUI_STATE") && "NOTPRESENT" == this.__gpdb.paramGet("MEDIA.DIGMAG.DRIVE1.GUI_STATE"))
            {
               _loc5_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
               _loc9_ = this.__gpdb.paramGetBoolean("MEDIA.DIGMAG.DRIVE0.FORMAT_REQUEST");
               _loc8_ = this.__gpdb.paramGetBoolean("MEDIA.DIGMAG.DRIVE1.FORMAT_REQUEST");
               if(_loc5_ == 2 && _loc9_)
               {
                  this.__textField_media1.text = "Internal";
                  this.__textField_media2.text = "";
                  this.__textField_media3.text = "Digital";
                  this.__textField_state1.text = "Magazine";
                  this.__textField_state2.text = "";
                  this.__textField_state3.text = "Formatting";
               }
               else if(_loc5_ == 2 && _loc8_)
               {
                  this.__textField_media1.text = "External";
                  this.__textField_media2.text = "";
                  this.__textField_media3.text = "Digital";
                  this.__textField_state1.text = "Magazine";
                  this.__textField_state2.text = "";
                  this.__textField_state3.text = "Formatting";
               }
               else
               {
                  this.__textField_media1.text = "Digital";
                  this.__textField_media2.text = "";
                  this.__textField_media3.text = "Magazine";
                  this.__textField_state1.text = "None";
                  this.__textField_state2.text = "";
                  this.__textField_state3.text = "Attached";
               }
            }
            else
            {
               _loc4_ = this.__mediaMgr.GetTargettedDrive();
               _loc7_ = this.__gpdb.paramGet("MEDIA.DIGMAG." + _loc4_ + ".GUI_STATE");
               this.__textField_media1.text = _loc4_ != "DRIVE0" ? "External" : "Internal";
               this.__textField_media2.text = "";
               this.__textField_media3.text = this.RecordingQualityString();
               switch(_loc7_)
               {
                  case "NOTPRESENT":
                     this["__notPresent" + _loc4_] = true;
                     this.__textField_state1.text = "";
                     this.__textField_state2.text = "Not Present";
                     this.__textField_state3.text = "";
                     break;
                  case "NOTMOUNTED":
                     this.__textField_state1.text = "";
                     this.__textField_state2.text = "Mounting...";
                     this.__textField_state3.text = "";
                     break;
                  case "UNMOUNTED":
                     this.__textField_state1.text = "Safe to";
                     this.__textField_state2.text = "";
                     this.__textField_state3.text = "Remove";
                     break;
                  case "EXPORTED":
                     this.__textField_state1.text = "Exported";
                     this.__textField_state2.text = "";
                     this.__textField_state3.text = "to PC";
                     break;
                  case "UNCONFIGURED":
                     this.__textField_state1.text = "";
                     this.__textField_state2.text = "Unformatted";
                     this.__textField_state3.text = "";
                     break;
                  case "INCOMPATIBLE":
                     this.__textField_state1.text = "Incompatible";
                     this.__textField_state2.text = "";
                     this.__textField_state3.text = "Project";
                     break;
                  case "MOUNTED":
                     if(!this.__gpdb.paramGetBoolean("MEDIA.DIGMAG.PROJECT_SETTINGS_RECORDABLE"))
                     {
                        this.__textField_state1.text = "Media is";
                        this.__textField_state2.text = "";
                        this.__textField_state3.text = "Too Slow";
                     }
                     else
                     {
                        this.__dmMounted = true;
                     }
                     break;
                  default:
                     _global.VxError("Widget_DigMag::UpdateDigmagVisual() Unknown drive state: " + _loc7_);
               }
            }
            break;
         default:
            this.__textField_media1.text = "Bad";
            this.__textField_media2.text = "";
            this.__textField_media3.text = "Media";
            this.__textField_state1.text = "";
            this.__textField_state2.text = "";
            this.__textField_state3.text = "";
      }
      var _loc3_ = this.__textField_media1.getTextFormat();
      _loc3_.align = "center";
      this.__textField_media1.setTextFormat(_loc3_);
      this.__textField_media2.setTextFormat(_loc3_);
      this.__textField_media3.setTextFormat(_loc3_);
      if(this.__dmMounted)
      {
         this.gotoAndStop(this.FRAME_MEDIA_PRESENT);
         this.PaintProjectInfo();
      }
      else
      {
         this.gotoAndStop(this.FRAME_NO_MEDIA);
      }
   }
   function Update(name, value)
   {
      var _loc4_;
      var _loc5_;
      var _loc6_;
      switch(name)
      {
         case "GUI.RUN_STATE":
            if(value == "GUI_STATE_3_INITIALIZE_GUI_STATE")
            {
               _loc4_ = this.__gpdb.paramGet("MEDIA.DIGMAG.ACTIVEDRIVE");
               if(_loc4_ != "NONE")
               {
                  _loc5_ = "MEDIA.DIGMAG." + _loc4_ + ".GUI_STATE";
                  _loc6_ = this.__gpdb.paramGet(_loc5_);
                  this.HandleDigmagState(_loc5_,_loc6_);
               }
            }
            return;
         case "MEDIA.DIGMAG.SELECTION_POLICY":
            this.UpdateDigmagVisual();
            return;
         case "PROJECT.PRIMARY_MEDIA":
            this.UpdateDigmagVisual();
            return;
         case "MEDIA.DIGMAG.PROJECT_SETTINGS_RECORDABLE":
            this.UpdateDigmagVisual();
            return;
         case "MEDIA.DIGMAG.TYPE":
            return;
         case "MEDIA.DIGMAG.DRIVE0.GUI_STATE":
         case "MEDIA.DIGMAG.DRIVE1.GUI_STATE":
            this.HandleDigmagState(name,value);
            return;
         case "MEDIA.DIGMAG.ACTIVEDRIVE":
            if(value != "NONE")
            {
               _loc5_ = "MEDIA.DIGMAG." + value + ".GUI_STATE";
               this.HandleDigmagState(_loc5_,this.__gpdb.paramGet(_loc5_));
            }
            return;
         case "MEDIA.DIGMAG.PROJECT.COMPRESSION":
            this.__dmCompression = value;
            this.UpdateDigmagVisual();
            return;
         case "MEDIA.DIGMAG.PROJECT.ENCODING":
            this.__dmEncoding = value;
            this.UpdateDigmagVisual();
            return;
         case "PROJECT.MODE_MATRIX.RESOLUTION":
            this.__dmResolution = value;
            this.UpdateDigmagVisual();
            return;
         case "MEDIA.DIGMAG.PROJECT.FRAME_RATE":
            this.__dmFrameRate = value;
            this.UpdateDigmagVisual();
            return;
         case "PROJECT.MODE_MATRIX.FRAME_RATE":
            this.UpdateDigmagVisual();
            return;
         case "PROJECT.MODE_MATRIX.COMPRESSION":
         case "PROJECT.MODE_MATRIX.ENCODING":
         case "PROJECT.MODE_MATRIX.QUALITY":
            this.UpdateDigmagVisual();
            return;
         default:
            return;
      }
   }
   function PaintProjectInfo()
   {
      var _loc2_;
      if(this.__dmMounted)
      {
         _loc2_ = "";
         this.gotoAndStop("FRAME_MEDIA_MOUNTED");
         switch(this.__dmEncoding)
         {
            case "RGB-progressive":
               this.__textField_encoding.text = "444";
               _loc2_ = "p";
               break;
            case "YCC-progressive":
               this.__textField_encoding.text = "422";
               _loc2_ = "p";
               break;
            case "RGB-interlaced":
               this.__textField_encoding.text = "444";
               _loc2_ = " i";
               break;
            case "YCC-interlaced":
               this.__textField_encoding.text = "422";
               _loc2_ = " i";
               break;
            case "REDCODE":
               this.__textField_encoding.text = "RAW";
               if(this.__dmResolution == "RGB1080P" || this.__dmResolution == "RGB720P")
               {
                  this.__textField_encoding.text = "RGB";
               }
               _loc2_ = "";
               break;
            default:
               this.__textField_encoding.text = "???";
         }
         switch(this.__dmResolution)
         {
            case "RGB1080P":
               this.__textField_format.text = "1080";
               break;
            case "RGB720P":
               this.__textField_format.text = "720";
               break;
            case "2K":
            case "3K":
            case "4K":
               this.__textField_format.text = this.__dmResolution;
               break;
            case "2K1.2:1":
               this.__textField_format.text = "2K AN";
               break;
            case "3K1.2:1":
               this.__textField_format.text = "3K AN";
               break;
            case "4K1.2:1":
               this.__textField_format.text = "4K AN";
               break;
            default:
               this.__textField_format.text = this.__dmResolution + _loc2_;
         }
         this.setFPS(this.__dmFrameRate);
         this._visible = true;
      }
   }
   function setFPS(value)
   {
      var _loc3_ = value.indexOf(".") != -1 ? value : value + ".00";
      this.__textField_fps.text = _loc3_;
   }
}

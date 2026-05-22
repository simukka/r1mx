class GUI.OSD_Components.ViewStatus extends GUI.OSD_Components.FullScreenMC
{
   var __gpdb;
   var __vsPTimeBase;
   var __vsQuality;
   var __vsPResolution;
   var __vsTimeDisp;
   var __vsMediaModel;
   var __vsMediaSerial;
   var __vsGenlock;
   var __vsJamSync;
   var __vsAudCh1;
   var __vsAudCh1Mode;
   var __vsAudCh1PP;
   var __vsAudCh1Level;
   var __vsAudCh2;
   var __vsAudCh2Mode;
   var __vsAudCh2PP;
   var __vsAudCh2Level;
   var __vsAudCh3;
   var __vsAudCh3Mode;
   var __vsAudCh3PP;
   var __vsAudCh3Level;
   var __vsAudCh4;
   var __vsAudCh4Mode;
   var __vsAudCh4PP;
   var __vsAudCh4Level;
   static var __vs;
   function ViewStatus()
   {
      super();
      this.__gpdb = _global.gpdb;
      GUI.OSD_Components.ViewStatus.__vs = this;
      GUI.OSD_Components.ViewStatus.__vs._visible = false;
      this.NewButton("OK",mx.utils.Delegate.create(this,this.cleanup),540,680);
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.ViewStatus.__vs === undefined)
      {
         _global.VxError("ViewStatus::GetManager(): ERROR! Called before created.");
      }
      return GUI.OSD_Components.ViewStatus.__vs;
   }
   function SmartView(vs)
   {
      if(vs == true)
      {
         GUI.OSD_Components.StatusLCD.GetManager().SetMenuTab("View Status");
         GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_ONESHOT);
         this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","false");
         this.Init();
         super.Activate();
      }
   }
   function cleanup()
   {
      GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
      this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","true");
      this.Deactivate(true);
   }
   function Init()
   {
      var _loc2_ = undefined;
      var _loc3_ = undefined;
      var _loc4_ = undefined;
      var _loc5_ = undefined;
      _loc2_ = this.__gpdb.paramGet("PROJECT.MODE_MATRIX.FRAME_RATE");
      this.__vsPTimeBase.text = _loc2_;
      _loc2_ = this.__gpdb.paramGet("PROJECT.MODE_MATRIX.QUALITY");
      this.__vsQuality.text = _loc2_;
      _loc2_ = this.__gpdb.paramGet("PROJECT.MODE_MATRIX.RESOLUTION");
      this.__vsPResolution.text = _loc2_;
      _loc2_ = this.__gpdb.paramGet("GUI.USER_PREF.TIMECODE_FORMAT");
      this.__vsTimeDisp.text = _loc2_;
      _loc5_ = this.__gpdb.paramGet("MEDIA.DIGMAG.ACTIVEDRIVE");
      if(_loc5_ == "NONE")
      {
         this.__vsMediaModel.text = "NO MEDIA";
         this.__vsMediaSerial.text = "NO MEDIA";
      }
      else
      {
         _loc2_ = this.__gpdb.paramGet("DIGITAL.MAGAZINE.MODEL_NUMBER");
         this.__vsMediaModel.text = _loc2_;
         _loc2_ = this.__gpdb.paramGet("DIGITAL.MAGAZINE.SERIAL_NUMBER");
         this.__vsMediaSerial.text = _loc2_;
      }
      _loc3_ = this.__gpdb.paramGetBoolean("SYSTEM.DEV.GENLOCK.REQUESTED");
      if(_loc3_)
      {
         this.__vsGenlock.text = "Yes";
      }
      else
      {
         this.__vsGenlock.text = "No";
      }
      _loc3_ = this.__gpdb.paramGetBoolean("SYSTEM.DEV.TIMECODE.JAMSYNC.REQUESTED");
      if(_loc3_)
      {
         this.__vsJamSync.text = "Yes";
      }
      else
      {
         this.__vsJamSync.text = "No";
      }
      _loc3_ = this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_1.ENABLE");
      if(_loc3_)
      {
         this.__vsAudCh1.text = "Yes";
      }
      else
      {
         this.__vsAudCh1.text = "No";
      }
      _loc2_ = this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_1.SOURCE");
      this.__vsAudCh1Mode.text = _loc2_;
      _loc3_ = this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_1.PHANTOM48V_ENABLE");
      if(_loc3_)
      {
         this.__vsAudCh1PP.text = "Yes";
      }
      else
      {
         this.__vsAudCh1PP.text = "No";
      }
      if(_loc2_ == "LINE")
      {
         _loc4_ = this.__gpdb.paramGetNumber("AUDIO.INPUT.CHANNEL_1.GAIN.LINE");
      }
      else
      {
         _loc4_ = this.__gpdb.paramGetNumber("AUDIO.INPUT.CHANNEL_1.GAIN.MICROPHONE");
      }
      this.__vsAudCh1Level.text = String(_loc4_);
      _loc3_ = this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_2.ENABLE");
      if(_loc3_)
      {
         this.__vsAudCh2.text = "Yes";
      }
      else
      {
         this.__vsAudCh2.text = "No";
      }
      _loc2_ = this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_2.SOURCE");
      this.__vsAudCh2Mode.text = _loc2_;
      _loc3_ = this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_2.PHANTOM48V_ENABLE");
      if(_loc3_)
      {
         this.__vsAudCh2PP.text = "Yes";
      }
      else
      {
         this.__vsAudCh2PP.text = "No";
      }
      if(_loc2_ == "LINE")
      {
         _loc4_ = this.__gpdb.paramGetNumber("AUDIO.INPUT.CHANNEL_2.GAIN.LINE");
      }
      else
      {
         _loc4_ = this.__gpdb.paramGetNumber("AUDIO.INPUT.CHANNEL_2.GAIN.MICROPHONE");
      }
      this.__vsAudCh2Level.text = String(_loc4_);
      _loc3_ = this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_3.ENABLE");
      if(_loc3_)
      {
         this.__vsAudCh3.text = "Yes";
      }
      else
      {
         this.__vsAudCh3.text = "No";
      }
      _loc2_ = this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_3.SOURCE");
      this.__vsAudCh3Mode.text = _loc2_;
      _loc3_ = this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_3.PHANTOM48V_ENABLE");
      if(_loc3_)
      {
         this.__vsAudCh3PP.text = "Yes";
      }
      else
      {
         this.__vsAudCh3PP.text = "No";
      }
      if(_loc2_ == "LINE")
      {
         _loc4_ = this.__gpdb.paramGetNumber("AUDIO.INPUT.CHANNEL_3.GAIN.LINE");
      }
      else
      {
         _loc4_ = this.__gpdb.paramGetNumber("AUDIO.INPUT.CHANNEL_3.GAIN.MICROPHONE");
      }
      this.__vsAudCh3Level.text = String(_loc4_);
      _loc3_ = this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_4.ENABLE");
      if(_loc3_)
      {
         this.__vsAudCh4.text = "Yes";
      }
      else
      {
         this.__vsAudCh4.text = "No";
      }
      _loc2_ = this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_4.SOURCE");
      this.__vsAudCh4Mode.text = _loc2_;
      _loc3_ = this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_4.PHANTOM48V_ENABLE");
      if(_loc3_)
      {
         this.__vsAudCh4PP.text = "Yes";
      }
      else
      {
         this.__vsAudCh4PP.text = "No";
      }
      if(_loc2_ == "LINE")
      {
         _loc4_ = this.__gpdb.paramGetNumber("AUDIO.INPUT.CHANNEL_4.GAIN.LINE");
      }
      else
      {
         _loc4_ = this.__gpdb.paramGetNumber("AUDIO.INPUT.CHANNEL_4.GAIN.MICROPHONE");
      }
      this.__vsAudCh4Level.text = String(_loc4_);
   }
}

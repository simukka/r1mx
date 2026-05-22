class GUI.OSD_Components.Widget_Timecode extends MovieClip
{
   var __gpdb;
   var __state;
   var __timecodeValue;
   var __projectFrameRate;
   var __timelapseEnabled;
   var __instantFrameRate;
   var __lastTime;
   var onEnterFrame;
   var __TIMECODE;
   var __tc_param = "VIDEO.TIMECODE.TIME_OF_DAY";
   var __autoCount = false;
   var __autoCountActive = false;
   function Widget_Timecode()
   {
      super();
      this.__gpdb = _global.gpdb;
      var _loc7_ = new Date();
      this.__state = null;
      this.FindCurrentFrameRate();
      this.addCallbacks();
      this.__autoCount = "true" == this.__gpdb.paramGet("GUI.OSD.TIMECODE.AUTO_COUNT");
      this.ConfigureTimcodeFormat();
      var _loc4_ = "true" == this.__gpdb.paramGet("PROJECT.MODE_MATRIX.DROPFRAME");
      var _loc6_ = false;
      var _loc5_ = this.__gpdb.paramGet("GUI.USER_PREF.TIMECODE_FORMAT") != "TIME" ? "E" : "T";
      this.__timecodeValue = new GUI.TimecodeValue(this.__gpdb.paramGet(this.__tc_param),this.__projectFrameRate,_loc4_,_loc6_,_loc5_);
      this.__timelapseEnabled = this.__gpdb.paramGetBoolean("GUI.RECORD.TIMELAPSE.ENABLED");
      this.StartFreeRun(this.__autoCount);
      this.Paint();
      this.SmartEnable();
   }
   function addCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.RecordingCallback);
      this.__gpdb.addCallback("GUI.USER_PREF.TIMECODE_FORMAT",_loc2_);
      this.__gpdb.addCallback("VIDEO.TIMECODE.TIME_OF_DAY",_loc2_);
      this.__gpdb.addCallback("VIDEO.TIMECODE.RUN_RECORD",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.MEDIA_PATH",_loc2_);
      this.__gpdb.addCallback("GUI.OSD.TIMECODE.AUTO_COUNT",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.MODE",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.STATE",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.REQUESTED",_loc2_);
      this.__gpdb.addCallback("VIDEO.MONITOR.TEST_PATTERN.ENABLED",_loc2_);
      this.__gpdb.addCallback("VIDEO.RECORD.FRAME_RATE.ACTUAL",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.FRAME_RATE",_loc2_);
      this.__gpdb.addCallback("PROJECT.MODE_MATRIX.DROPFRAME",_loc2_);
      this.__gpdb.addCallback("GUI.RECORD.TIMELAPSE.ENABLED",_loc2_);
   }
   function FindCurrentFrameRate()
   {
      this.__projectFrameRate = Number(this.__gpdb.paramGet("PROJECT.MODE_MATRIX.FRAME_RATE"));
      this.__instantFrameRate = Number(this.__gpdb.paramGet("VIDEO.RECORD.FRAME_RATE.ACTUAL"));
   }
   function RecordingCallback(name, value)
   {
      switch(name)
      {
         case "GUI.RECORD.TIMELAPSE.ENABLED":
            this.__gpdb.paramSet("GUI.OSD.TIMECODE.AUTO_COUNT",value == "false");
            this.__timelapseEnabled = value == "true";
            break;
         case "GUI.USER_PREF.TIMECODE_FORMAT":
            this.ConfigureTimcodeFormat();
            this.__timecodeValue.SetPrefix(value != "TIME" ? "E" : "T");
            this.DisplayNewTimecode(this.__gpdb.paramGet(this.__tc_param),value != "TIME" ? false : true);
            break;
         case "VIDEO.TIMECODE.TIME_OF_DAY":
            if(name == this.__tc_param)
            {
               this.DisplayNewTimecode(value,this.__gpdb.paramGet("GUI.USER_PREF.TIMECODE_FORMAT") != "TIME" ? false : true);
            }
            break;
         case "VIDEO.TIMECODE.RUN_RECORD":
            if(name == this.__tc_param)
            {
               this.DisplayNewTimecode(value,this.__gpdb.paramGet("GUI.USER_PREF.TIMECODE_FORMAT") != "TIME" ? false : true);
            }
            break;
         case "GUI.OSD.TIMECODE.AUTO_COUNT":
            this.__autoCount = value == "true";
            break;
         case "VIDEO.RECORD.REQUESTED":
            if(value == "true")
            {
               this.__state = "REC";
            }
            else
            {
               if(this.__autoCount)
               {
                  this.StopFreeRun();
               }
               this.__state = "POST";
            }
            this.Paint();
            break;
         case "VIDEO.RECORD.MODE":
            this.Paint();
            break;
         case "VIDEO.RECORD.STATE":
            if(this.__autoCount)
            {
               if(value == "ACTIVE")
               {
                  if("CONTINUOUS" == this.__gpdb.paramGet("VIDEO.RECORD.MODE"))
                  {
                     this.StartFreeRun(this.__autoCount);
                  }
               }
               else
               {
                  this.StopFreeRun();
                  this.__timecodeValue.SetStringValue(this.__gpdb.paramGet(this.__tc_param));
               }
            }
            else
            {
               this.__timecodeValue.SetStringValue(this.__gpdb.paramGet(this.__tc_param));
            }
            this.__state = null;
            this.DisplayNewTimecode(this.__gpdb.paramGet(this.__tc_param),this.__gpdb.paramGet("GUI.USER_PREF.TIMECODE_FORMAT") != "TIME" ? false : true);
            this.Paint();
            break;
         case "MEDIA.DIGMAG.MEDIA_PATH":
         case "VIDEO.MONITOR.TEST_PATTERN.ENABLED":
         case "VIDEO.PLAYBACK.STATE":
            this.SmartEnable();
         case "VIDEO.RECORD.FRAME_RATE.ACTUAL":
            if(this.__autoCount)
            {
               this.AutoCounter();
            }
            this.__instantFrameRate = Number(value);
            break;
         case "PROJECT.MODE_MATRIX.FRAME_RATE":
            this.__timecodeValue.SetRate(Number(value));
            break;
         case "PROJECT.MODE_MATRIX.DROPFRAME":
            this.__timecodeValue.SetDropFrame(value == "true");
      }
   }
   function DisplayNewTimecode(tc, run)
   {
      this.__timecodeValue.SetStringValue(tc);
      if(run)
      {
         if(this.__timelapseEnabled)
         {
            if(this.__gpdb.paramGet("VIDEO.RECORD.STATE") == "ACTIVE")
            {
               this.__timecodeValue.SetStringValue(this.__gpdb.paramGet(this.__tc_param));
               this.StopFreeRun();
            }
            else
            {
               this.StartFreeRun(true);
            }
         }
         else
         {
            this.StartFreeRun(this.__autoCount);
         }
      }
      else if(this.__gpdb.paramGet("VIDEO.RECORD.STATE") == "ACTIVE")
      {
         this.StartFreeRun(this.__autoCount);
      }
      else
      {
         this.StopFreeRun();
      }
      this.Paint();
   }
   function StartFreeRun(bVal)
   {
      if(bVal)
      {
         this.__autoCountActive = true;
         this.__lastTime = getTimer();
         this.__timecodeValue.SetStringValue(this.__gpdb.paramGet(this.__tc_param));
         this.FindCurrentFrameRate();
         this.__timecodeValue.SetRate(this.__projectFrameRate);
         this.onEnterFrame = this.AutoCounter;
      }
   }
   function StopFreeRun()
   {
      this.__autoCountActive = false;
      this.onEnterFrame = null;
   }
   function StopAt(tc)
   {
   }
   function Paint()
   {
      var _loc2_ = undefined;
      switch(this.__gpdb.paramGet("VIDEO.RECORD.STATE"))
      {
         case "ACTIVE":
            _loc2_ = 16711680;
            break;
         case "PRERECORD":
            _loc2_ = 16776960;
            break;
         default:
            _loc2_ = 16777215;
      }
      if(this.__state === null)
      {
         if(this.__timecodeValue.GetString(true) != "T NaN:NaN:NaN:NaN")
         {
            this.__TIMECODE.text = this.__timecodeValue.GetString(true);
         }
      }
      else
      {
         this.__TIMECODE.text = this.__state;
      }
      var _loc3_ = this.__TIMECODE.getTextFormat();
      _loc3_.color = _loc2_;
      this.__TIMECODE.setTextFormat(_loc3_);
   }
   function SmartEnable()
   {
      var _loc4_ = "" == this.__gpdb.paramGet("MEDIA.DIGMAG.MEDIA_PATH");
      var _loc5_ = "true" == this.__gpdb.paramGet("VIDEO.MONITOR.TEST_PATTERN.ENABLED");
      var _loc3_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc2_ = !_loc4_ && !_loc5_ && !_loc3_;
      if(_loc2_)
      {
         this.DisplayNewTimecode(this.__gpdb.paramGet(this.__tc_param),this.__gpdb.paramGet("GUI.USER_PREF.TIMECODE_FORMAT") != "TIME" ? false : true);
      }
      this._visible = _loc2_;
   }
   function AutoCounter()
   {
      if(this.__autoCountActive)
      {
         var _loc2_ = getTimer();
         var _loc3_ = _loc2_ - this.__lastTime;
         var _loc5_ = this.__instantFrameRate / this.__timecodeValue.GetRate();
         var _loc4_ = this.__timecodeValue.AdvanceMS(_loc3_,_loc5_);
         this.__lastTime = _loc2_ - _loc4_;
         this.Paint();
      }
   }
   function ConfigureTimcodeFormat()
   {
      if(this.__gpdb.paramGet("GUI.USER_PREF.TIMECODE_FORMAT") == "TIME")
      {
         this.__tc_param = "VIDEO.TIMECODE.TIME_OF_DAY";
      }
      else
      {
         this.__tc_param = "VIDEO.TIMECODE.RUN_RECORD";
      }
   }
   function DEBUG(str)
   {
      if(_global.VxLog)
      {
         str = "GUI TIMECODE >> " + str;
         _global.VxLog(str);
      }
      else
      {
         str = "GUI TIMECODE >> " + str;
      }
   }
}

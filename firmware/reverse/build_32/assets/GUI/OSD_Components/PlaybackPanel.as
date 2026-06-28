class GUI.OSD_Components.PlaybackPanel extends GUI.OSD_Components.Gadget
{
   var BLACKOUT_E;
   var BLACKOUT_N;
   var BLACKOUT_S;
   var BLACKOUT_W;
   var __clip;
   var __clipNameLabel;
   var __clipNameLabelShadow;
   var __clips;
   var __currentTimecodeLabel;
   var __gpdb;
   var __i;
   var __indicator;
   var __indicatorText;
   var __interval;
   var __playhead;
   var __playheadX0;
   var __positionLabel;
   var __t;
   var __timeFactor;
   var __timecodeLabel;
   var __timecodeLabelShadow;
   var _visible;
   static var __manager;
   var PROGRESS_BAR_WIDTH = 966;
   var PLAYBACK_MODE_NORMAL = "PLAY";
   var PLAYBACK_MODE_PAUSED = "PAUSE";
   var PLAYBACK_MODE_RR_1X = "RR_1X";
   var PLAYBACK_MODE_RR_2X = "RR_2X";
   var PLAYBACK_MODE_RR_8X = "RR_8X";
   var PLAYBACK_MODE_RR_32X = "RR_32X";
   var PLAYBACK_MODE_FF_2X = "FF_2X";
   var PLAYBACK_MODE_FF_8X = "FF_8X";
   var PLAYBACK_MODE_FF_32X = "FF_32X";
   var PLAYBACK_MODE_POSTROLL = "POSTROLL";
   var PLAYBACK_STATE_IDLE = "IDLE";
   var PLAYBACK_STATE_ERROR = "ERROR";
   var PLAYBACK_STATE_NORMAL = "PLAY";
   var PLAYBACK_STATE_PAUSED = "PAUSE";
   var PLAYBACK_STATE_RR_1X = "RR_1X";
   var PLAYBACK_STATE_RR_2X = "RR_2X";
   var PLAYBACK_STATE_RR_8X = "RR_8X";
   var PLAYBACK_STATE_RR_32X = "RR_32X";
   var PLAYBACK_STATE_FF_2X = "FF_2X";
   var PLAYBACK_STATE_FF_8X = "FF_8X";
   var PLAYBACK_STATE_FF_32X = "FF_32X";
   var PLAYBACK_STATE_POSTROLL = "POSTROLL";
   var PLAYBACK_JUMP_START = "BEGINNING";
   var PLAYBACK_JUMP_END = "END";
   var PLAYBACK_JUMP_NEXT_FRAME = "NEXT_FRAME";
   var PLAYBACK_JUMP_PREV_FRAME = "PREV_FRAME";
   function PlaybackPanel()
   {
      super();
      _global.VxDebug("...........................................................................CTOR PlaybackPanel()");
      GUI.OSD_Components.PlaybackPanel.__manager = this;
      this._visible = false;
      this.__indicatorText._visible = false;
      this.__playheadX0 = this.__playhead._x;
      this.__gpdb = _global.gpdb;
      this.BLACKOUT_N._visible = false;
      this.BLACKOUT_S._visible = false;
      this.BLACKOUT_E._visible = false;
      this.BLACKOUT_W._visible = false;
      this.__clips = [];
      this.__i = 0;
      this.__state = null;
      this.__timeFactor = 0;
      this.__interval = 0;
      this.StopTimer();
      this.SetClips(this.__gpdb.paramGet("MEDIA.DIGMAG.CLIP_LIST"));
      this.SetState(this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE"));
      this.InitCallbacks();
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.PlaybackPanel.__manager === undefined)
      {
         _global.VxError("PlaybackPanel::GetManager() called before instantiated!");
      }
      return GUI.OSD_Components.PlaybackPanel.__manager;
   }
   function SetClips(clips)
   {
      this.__clips = [];
      if(clips)
      {
         this.__clips = clips.split(",");
      }
      var _loc3_ = 0;
      var _loc2_;
      while(_loc3_ < this.__clips.length)
      {
         _loc2_ = this.__clips[_loc3_];
         if(_loc2_.substr(_loc2_.length - 4,4) == ".RDC")
         {
            this.__clips[_loc3_] = _loc2_.substr(0,_loc2_.length - 4);
         }
         _loc3_ = _loc3_ + 1;
      }
      if(this.__clip)
      {
         this.FindClipInList(this.__clip.name);
      }
   }
   function FindClipInList(clipName)
   {
      var _loc2_ = 0;
      while(_loc2_ < this.__clips.length)
      {
         if(this.__clips[_loc2_] == clipName)
         {
            this.__i = _loc2_;
            return undefined;
         }
         _loc2_ = _loc2_ + 1;
      }
   }
   function SetState(state)
   {
      var _loc4_ = this.__state;
      this.__state = state;
      var _loc2_;
      switch(state)
      {
         case this.PLAYBACK_STATE_NORMAL:
         case this.PLAYBACK_STATE_PAUSED:
         case this.PLAYBACK_STATE_RR_1X:
         case this.PLAYBACK_STATE_RR_2X:
         case this.PLAYBACK_STATE_RR_8X:
         case this.PLAYBACK_STATE_RR_32X:
         case this.PLAYBACK_STATE_FF_2X:
         case this.PLAYBACK_STATE_FF_8X:
         case this.PLAYBACK_STATE_FF_32X:
            if(!this.IsOpen())
            {
               this.ShowPanel();
            }
            if(!this.__clip)
            {
               this.BuildCurrentClip();
               _loc2_ = parseInt(this.__gpdb.paramGet("VIDEO.PLAYBACK.CURRENTFRAME"));
               if(isNaN(_loc2_))
               {
                  _loc2_ = 0;
               }
               this.__clip.SetCurrentFrame(_loc2_);
               this.PositionPlayhead();
               this.StartTimer();
            }
            else if(this.__t < 0)
            {
               this.StartTimer();
            }
      }
      this.UpdateProgress();
      switch(state)
      {
         case this.PLAYBACK_STATE_NORMAL:
            this.__indicator.gotoAndStop("play");
            this.__indicatorText._visible = false;
            this.__timeFactor = 1;
            return;
         case this.PLAYBACK_STATE_PAUSED:
            this.__indicator.gotoAndStop("pause");
            this.__indicatorText._visible = false;
            this.__timeFactor = 0;
            return;
         case this.PLAYBACK_STATE_RR_1X:
            this.__indicator.gotoAndStop("fr");
            this.__indicatorText.text = "1x";
            this.__indicatorText._visible = true;
            this.__timeFactor = -1;
            return;
         case this.PLAYBACK_STATE_RR_2X:
            this.__indicator.gotoAndStop("fr");
            this.__indicatorText.text = "2x";
            this.__indicatorText._visible = true;
            this.__timeFactor = -2;
            return;
         case this.PLAYBACK_STATE_RR_8X:
            this.__indicator.gotoAndStop("fr");
            this.__indicatorText.text = "8x";
            this.__indicatorText._visible = true;
            this.__timeFactor = -8;
            return;
         case this.PLAYBACK_STATE_RR_32X:
            this.__indicator.gotoAndStop("fr");
            this.__indicatorText.text = "32x";
            this.__indicatorText._visible = true;
            this.__timeFactor = -32;
            return;
         case this.PLAYBACK_STATE_FF_2X:
            this.__indicator.gotoAndStop("ff");
            this.__indicatorText.text = "2x";
            this.__indicatorText._visible = true;
            this.__timeFactor = 2;
            return;
         case this.PLAYBACK_STATE_FF_8X:
            this.__indicator.gotoAndStop("ff");
            this.__indicatorText.text = "8x";
            this.__indicatorText._visible = true;
            this.__timeFactor = 8;
            return;
         case this.PLAYBACK_STATE_FF_32X:
            this.__indicator.gotoAndStop("ff");
            this.__indicatorText.text = "32x";
            this.__indicatorText._visible = true;
            this.__timeFactor = 32;
            return;
         case this.PLAYBACK_STATE_POSTROLL:
            return;
         case this.PLAYBACK_STATE_ERROR:
            this.HandlePlaybackError();
            this.DeactivatePlayback();
            this.__gpdb.paramSet("VIDEO.PLAYBACK.STATE",this.PLAYBACK_STATE_IDLE);
            return;
         case this.PLAYBACK_STATE_IDLE:
            this.HidePanel();
      }
      this.__timeFactor = 0;
      this.StopTimer();
      this.__clip = null;
      this.__indicator.gotoAndStop("blank");
      this.__indicatorText._visible = false;
      this.__state = null;
      this.PositionPlayhead();
   }
   function InitCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.HandleParamCallback);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.REQUESTED",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.CLIPPARAMS",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.CLIP_LIST",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.CURRENTFRAME",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.DRIVE0.GUI_STATE",_loc2_);
      this.__gpdb.addCallback("MEDIA.DIGMAG.DRIVE1.GUI_STATE",_loc2_);
      var _loc3_ = mx.utils.Delegate.create(this,this.HandlePlaybackButton);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.PLAYBACK.PREV_CLIP",_loc3_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.PLAYBACK.RR",_loc3_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.PLAYBACK.PLAY",_loc3_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.PLAYBACK.FF",_loc3_);
      this.__gpdb.addCallback("GUI.RAWINPUT.BUTTON.PLAYBACK.NEXT_CLIP",_loc3_);
      this.__gpdb.addCallback("SYSTEM.DEV.SUPERGRIP.RAWINPUT.BUTTON.BAL",_loc3_);
   }
   function HandleParamCallback(param, value)
   {
      var _loc4_;
      switch(param)
      {
         case "VIDEO.PLAYBACK.REQUESTED":
            GUI.OSD_Components.RecordManager.GetManager().SelectivelyEnableMagnification(false);
            return;
         case "VIDEO.PLAYBACK.STATE":
            this.SetState(value);
            return;
         case "MEDIA.DIGMAG.CLIP_LIST":
            this.SetClips(value);
            return;
         case "VIDEO.PLAYBACK.CLIPPARAMS":
            if(value != "")
            {
               if("IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE"))
               {
                  this.HandlePlaybackParams();
               }
            }
            return;
         case "VIDEO.PLAYBACK.CURRENTFRAME":
            if("CUED" == this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_1.TRIGGER"))
            {
               this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_1",value == "0");
            }
            if("CUED" == this.__gpdb.paramGet("SYSTEM.DEV.GPIO.CONFIG.OUTPUT_2.TRIGGER"))
            {
               this.__gpdb.paramSet("SYSTEM.DEV.GPIO.SETTING.OUTPUT_2",value == "0");
            }
            if(this.__clip)
            {
               _loc4_ = parseInt(value);
               if(isNaN(_loc4_))
               {
                  _loc4_ = 0;
               }
               this.__clip.SetCurrentFrame(_loc4_);
               this.PositionPlayhead();
               this.StartTimer();
            }
            return;
         case "MEDIA.DIGMAG.DRIVE0.GUI_STATE":
         case "MEDIA.DIGMAG.DRIVE1.GUI_STATE":
            if(value != "MOUNTED")
            {
               this.__gpdb.paramSet("VIDEO.PLAYBACK.REQUESTED",false);
            }
            return;
         default:
            _global.VxLog("ERROR. PlaybackPanel::HandleParamCallback(" + param + ", " + value + ") Not handled.");
            return;
      }
   }
   function DEBUG(str)
   {
      if(_global.VxLog)
      {
         str = "PLAYBACK >> " + str;
         _global.VxLog(str);
      }
      else
      {
         str = "*\n** PLAYBACK >> " + str + "\n*";
      }
   }
   function IsPlayingForward()
   {
      switch(this.__state)
      {
         case this.PLAYBACK_STATE_NORMAL:
         case this.PLAYBACK_STATE_FF_2X:
         case this.PLAYBACK_STATE_FF_8X:
         case this.PLAYBACK_STATE_FF_32X:
            return true;
         default:
            return false;
      }
   }
   function IsPlayingReverse()
   {
      switch(this.__state)
      {
         case this.PLAYBACK_STATE_RR_1X:
         case this.PLAYBACK_STATE_RR_2X:
         case this.PLAYBACK_STATE_RR_8X:
         case this.PLAYBACK_STATE_RR_32X:
            return true;
         default:
            return false;
      }
   }
   function HandlePlaybackButton(param, value)
   {
      _global.VxDebug("PlaybackPanel::HandlePlaybackButton(" + param + " = " + value + ")");
      var _loc5_ = GUI.OSD_Components.RecordManager.GetManager().IsRecording();
      var _loc6_ = value != "true";
      var _loc3_;
      if(!_loc5_ && _loc6_)
      {
         switch(param)
         {
            case "GUI.RAWINPUT.BUTTON.PLAYBACK.PLAY":
               this.HandlePlayClipRequest();
               break;
            case "GUI.RAWINPUT.BUTTON.PLAYBACK.PREV_CLIP":
               this.RequestPause();
               if(this.__clip.GetProgress() == 0)
               {
                  this.RequestPrev();
               }
               else
               {
                  this.RequestStart();
               }
               break;
            case "GUI.RAWINPUT.BUTTON.PLAYBACK.RR":
               _loc3_ = this.GetNextRRSpeed();
               if(_loc3_ > 0)
               {
                  this.RequestRR(_loc3_);
               }
               else
               {
                  this.RequestPlay();
               }
               break;
            case "GUI.RAWINPUT.BUTTON.PLAYBACK.FF":
               _loc3_ = this.GetNextFFSpeed();
               if(_loc3_ > 0)
               {
                  this.RequestFF(_loc3_);
               }
               else
               {
                  this.RequestPlay();
               }
               break;
            case "GUI.RAWINPUT.BUTTON.PLAYBACK.NEXT_CLIP":
               this.HandleNextClipRequest();
               break;
            case "SYSTEM.DEV.SUPERGRIP.RAWINPUT.BUTTON.BAL":
               if(this.IsOpen())
               {
                  this.DeactivatePlayback();
               }
               else
               {
                  this.ActivatePlayback();
                  this.RequestPlay();
               }
            default:
               return;
         }
      }
   }
   function HandlePlayClipRequest()
   {
      if(this.IsOpen())
      {
         if(this.__state == this.PLAYBACK_STATE_PAUSED)
         {
            if(this.__clip && this.__clip.GetProgress() == 1)
            {
               this.RequestStart();
            }
            this.RequestPlay();
         }
         else if(this.__state == this.PLAYBACK_STATE_NORMAL)
         {
            this.RequestPause();
         }
         else
         {
            this.RequestPlay();
         }
      }
      else
      {
         this.ActivatePlayback();
      }
   }
   function HandleNextClipRequest()
   {
      this.RequestPause();
      if(this.__clip.EndOfClip() == true)
      {
         this.RequestNext();
      }
      else
      {
         this.RequestEnd();
      }
   }
   function HandleOpenAndPlayOnce()
   {
      _global.VxLog("PlaybackPanel::HandleOpenAndPlayOnce() Unimplemented.");
   }
   function ShowPanel()
   {
      this._visible = true;
      this.__interval = setInterval(mx.utils.Delegate.create(this,this.UpdateProgress),50);
   }
   function HidePanel()
   {
      clearInterval(this.__interval);
      this.__interval = 0;
      this._visible = false;
      GUI.OSD_Components.StatusLCD.GetManager().SetPane("FRAME_STATUS");
   }
   function IsOpen()
   {
      return this._visible;
   }
   function ActivatePlayback()
   {
      if(this.__gpdb.paramGetBoolean("MEDIA.DIGMAG.PROJECT_IS_COMPATIBLE"))
      {
         if(this.__clips.length > 0)
         {
            this.__i = this.__clips.length - 1;
            this.RequestPause();
            this.__gpdb.paramSet("VIDEO.PLAYBACK.CLIPNAME",this.__clips[this.__i]);
            this.__gpdb.paramSet("VIDEO.PLAYBACK.REQUESTED",true);
            GpioManager.GetManager().FlagPlaybackState(true);
         }
      }
   }
   function DeactivatePlayback()
   {
      this.__gpdb.paramSet("VIDEO.PLAYBACK.REQUESTED",false);
      GpioManager.GetManager().FlagPlaybackState(true);
   }
   function HandlePlaybackError()
   {
      var _loc2_ = this.__gpdb.paramGet("SYSTEM.ERROR.PLAYBACK");
      GUI.OSD_Components.ErrorManagerMC.GetManager().PopupErrorMessage("Playback Error: ",_loc2_);
   }
   function RequestPlay()
   {
      if(this.PLAYBACK_MODE_NORMAL == this.__gpdb.paramGet("VIDEO.PLAYBACK.TRICKMODE"))
      {
         this.RequestPause();
      }
      this.__gpdb.paramSet("VIDEO.PLAYBACK.TRICKMODE",this.PLAYBACK_MODE_NORMAL);
   }
   function RequestPause()
   {
      this.__gpdb.paramSet("VIDEO.PLAYBACK.TRICKMODE",this.PLAYBACK_MODE_PAUSED);
   }
   function GetNextFFSpeed()
   {
      switch(this.__state)
      {
         case this.PLAYBACK_STATE_RR_1X:
         case this.PLAYBACK_STATE_RR_2X:
         case this.PLAYBACK_STATE_RR_8X:
         case this.PLAYBACK_STATE_RR_32X:
         case this.PLAYBACK_STATE_PAUSED:
         case this.PLAYBACK_STATE_NORMAL:
            return 2;
         case this.PLAYBACK_STATE_FF_2X:
            return 8;
         case this.PLAYBACK_STATE_FF_8X:
            return 32;
         case this.PLAYBACK_STATE_FF_32X:
         default:
            return 0;
      }
   }
   function RequestFF(speed)
   {
      var _loc3_ = null;
      switch(speed)
      {
         case 2:
            _loc3_ = this.PLAYBACK_MODE_FF_2X;
            break;
         case 8:
            _loc3_ = this.PLAYBACK_MODE_FF_8X;
            break;
         case 32:
            _loc3_ = this.PLAYBACK_MODE_FF_32X;
            break;
         default:
            _global.VxLog("ERROR. PlaybackPanel::RequestFF(" + speed + ") Unknown.");
      }
      if(_loc3_ != null)
      {
         this.__gpdb.paramSet("VIDEO.PLAYBACK.TRICKMODE",_loc3_);
      }
   }
   function GetNextRRSpeed()
   {
      switch(this.__state)
      {
         case this.PLAYBACK_STATE_FF_2X:
         case this.PLAYBACK_STATE_FF_8X:
         case this.PLAYBACK_STATE_FF_32X:
         case this.PLAYBACK_STATE_PAUSED:
         case this.PLAYBACK_STATE_NORMAL:
            return 1;
         case this.PLAYBACK_STATE_RR_1X:
            return 2;
         case this.PLAYBACK_STATE_RR_2X:
            return 8;
         case this.PLAYBACK_STATE_RR_8X:
            return 0;
         case this.PLAYBACK_STATE_RR_32X:
         default:
            return 0;
      }
   }
   function RequestRR(speed)
   {
      var _loc3_ = null;
      switch(speed)
      {
         case 1:
            _loc3_ = this.PLAYBACK_MODE_RR_1X;
            break;
         case 2:
            _loc3_ = this.PLAYBACK_MODE_RR_2X;
            break;
         case 8:
            _loc3_ = this.PLAYBACK_MODE_RR_8X;
            break;
         case 32:
            _loc3_ = this.PLAYBACK_MODE_RR_32X;
            break;
         default:
            _global.VxLog("ERROR. PlaybackPanel::RequestRR(" + speed + ") Unknown.");
      }
      if(_loc3_ != null)
      {
         this.__gpdb.paramSet("VIDEO.PLAYBACK.TRICKMODE",_loc3_);
      }
   }
   function RequestStart()
   {
      this.__gpdb.paramSet("VIDEO.PLAYBACK.JUMP",this.PLAYBACK_JUMP_START);
   }
   function RequestEnd()
   {
      this.__gpdb.paramSet("VIDEO.PLAYBACK.JUMP",this.PLAYBACK_JUMP_END);
   }
   function RequestPrev()
   {
      if(this.__i > 0)
      {
         this.__i = this.__i - 1;
         this.__gpdb.paramSet("VIDEO.PLAYBACK.CLIPNAME",this.__clips[this.__i]);
      }
   }
   function RequestNext()
   {
      if(this.__i < this.__clips.length - 1)
      {
         this.__i = this.__i + 1;
         this.__gpdb.paramSet("VIDEO.PLAYBACK.CLIPNAME",this.__clips[this.__i]);
      }
   }
   function RequestNextFrame()
   {
      this.__gpdb.paramSet("VIDEO.PLAYBACK.JUMP",this.PLAYBACK_JUMP_NEXT_FRAME);
   }
   function RequestPrevFrame()
   {
      this.__gpdb.paramSet("VIDEO.PLAYBACK.JUMP",this.PLAYBACK_JUMP_PREV_FRAME);
   }
   function RequestJumpForward()
   {
      var _loc3_ = this.__clip.GetProgress() * 100 + 2;
      var _loc2_;
      if(_loc3_ >= 80)
      {
         _loc2_ = "END";
      }
      else if(_loc3_ >= 60)
      {
         _loc2_ = "80Percent";
      }
      else if(_loc3_ >= 40)
      {
         _loc2_ = "60Percent";
      }
      else if(_loc3_ >= 20)
      {
         _loc2_ = "40Percent";
      }
      else
      {
         _loc2_ = "20Percent";
      }
      this.__gpdb.paramSet("VIDEO.PLAYBACK.JUMP",_loc2_);
   }
   function RequestJumpBackward()
   {
      var _loc3_ = this.__clip.GetProgress() * 100 - 2;
      var _loc2_;
      if(_loc3_ <= 20)
      {
         _loc2_ = "BEGINNING";
      }
      else if(_loc3_ <= 40)
      {
         _loc2_ = "20Percent";
      }
      else if(_loc3_ <= 60)
      {
         _loc2_ = "40Percent";
      }
      else if(_loc3_ <= 80)
      {
         _loc2_ = "60Percent";
      }
      else
      {
         _loc2_ = "80Percent";
      }
      this.__gpdb.paramSet("VIDEO.PLAYBACK.JUMP",_loc2_);
   }
   function HandlePlaybackParams()
   {
      this.BuildCurrentClip();
   }
   function BuildCurrentClip()
   {
      var _loc4_ = {};
      var _loc5_ = this.__gpdb.paramGet("VIDEO.PLAYBACK.CLIPPARAMS").split(";");
      var _loc2_ = 0;
      var _loc3_;
      while(_loc2_ < _loc5_.length)
      {
         _loc3_ = _loc5_[_loc2_].split("=");
         _loc4_[_loc3_[0]] = _loc3_[1];
         _loc2_ = _loc2_ + 1;
      }
      var _loc6_;
      var _loc11_ = "E";
      var _loc9_ = this.__gpdb.paramGet("GUI.USER_PREF.TIMECODE_FORMAT");
      if(_loc9_ == "EDGE")
      {
         _loc6_ = _loc4_.FIRSTTIMECODERR;
      }
      else
      {
         _loc11_ = "T";
         _loc6_ = _loc4_.FIRSTTIMECODEVITC;
      }
      var _loc10_ = false;
      var _loc8_ = new GUI.TimecodeValue(_loc6_,_loc4_.FRAMERATE,_loc10_,false,_loc11_);
      if(_loc9_ == "EDGE" && _loc8_.GetFramesSinceZero() == 0)
      {
         _loc8_ = new GUI.TimecodeValue(_loc4_.FIRSTTIMECODEVITC,_loc4_.FRAMERATE,_loc10_,false,"T");
      }
      var _loc7_ = parseInt(_loc4_.NUMVIDFRAMES);
      if(isNaN(_loc7_))
      {
         _loc7_ = 0;
      }
      this.__clip = new GUI.OSD_Components.Clip(_loc4_.CLIPNAME,_loc8_,_loc7_);
      _loc6_ = this.__clip.timecode.GetString(true);
      this.__timecodeLabel.text = _loc6_;
      this.__timecodeLabelShadow.text = _loc6_;
      this.__clipNameLabel.text = this.__clip.name;
      this.__clipNameLabelShadow.text = this.__clip.name;
      var _loc12_ = this.__clip.name.lastIndexOf("_");
      var _loc13_ = this.__clip.name.substr(0,_loc12_);
      GUI.OSD_Components.StatusLCD.GetManager().GotoPlayback(_loc13_,_loc6_);
      this.__currentTimecodeLabel.text = _loc6_;
      this.FindClipInList(this.__clip.name);
      if(this.__clips.length <= 0)
      {
         this.__positionLabel.text = "";
      }
      else
      {
         this.__positionLabel.text = this.__i + 1 + " of " + this.__clips.length;
      }
   }
   function PositionPlayhead()
   {
      var _loc2_;
      if(this.__clip)
      {
         _loc2_ = this.__clip.GetProgress() * this.PROGRESS_BAR_WIDTH;
         this.__playhead._x = this.__playheadX0 + _loc2_;
         this.__currentTimecodeLabel.text = this.__clip.timecode.GetString(true);
      }
      else
      {
         this.__playhead._x = this.__playheadX0;
         this.__currentTimecodeLabel.text = "";
      }
   }
   function StartTimer()
   {
      this.__t = getTimer();
   }
   function StopTimer()
   {
      this.__t = -1;
   }
   function UpdateProgress()
   {
      var _loc2_;
      var _loc3_;
      var _loc4_;
      if(this.__clip && this.__t >= 0)
      {
         _loc2_ = getTimer();
         _loc3_ = _loc2_ - this.__t;
         this.__t = _loc2_;
         if(this.__timeFactor != 0)
         {
            _loc4_ = this.__clip.timecode.AdvanceMS(_loc3_,this.__timeFactor);
            this.__t -= _loc4_;
            this.PositionPlayhead();
         }
      }
   }
   function onEnterFrame()
   {
      if(this._visible)
      {
         this.UpdateProgress();
      }
   }
   function Activate(enable)
   {
      _global.VxDebug("PlaybakcPanel::Activate(" + enable.toString() + ")");
   }
   function getTabTargets()
   {
      return [];
   }
   function onInputEvent(name, value)
   {
      var _loc3_ = false;
      var _loc6_ = value == "true";
      _global.VxDebug("...PlaybackPanel::onInputEvent(): " + name + "," + value);
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_EXIT:
            if(_loc6_)
            {
               this.DeactivatePlayback();
            }
            _loc3_ = true;
            break;
         case GUI.OSD_Components.TabManager.EVENT_LEFT:
            if(this.__state == this.PLAYBACK_STATE_PAUSED)
            {
               this.RequestPrevFrame();
               _loc3_ = true;
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_RIGHT:
            if(this.__state == this.PLAYBACK_STATE_PAUSED)
            {
               this.RequestNextFrame();
               _loc3_ = true;
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CCW:
            this.RequestPause();
            if(this.__clip.GetProgress() == 0)
            {
               this.RequestPrev();
            }
            else
            {
               this.RequestStart();
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CW:
            this.HandleNextClipRequest();
            break;
         case GUI.OSD_Components.TabManager.EVENT_CCW_JUMP:
            if(this.__state == this.PLAYBACK_STATE_PAUSED)
            {
               this.RequestJumpBackward();
               _loc3_ = true;
            }
            break;
         case GUI.OSD_Components.TabManager.EVENT_CW_JUMP:
            if(this.__state == this.PLAYBACK_STATE_PAUSED)
            {
               this.RequestJumpForward();
               _loc3_ = true;
            }
      }
      return _loc3_;
   }
}

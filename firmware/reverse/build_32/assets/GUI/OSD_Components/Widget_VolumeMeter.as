class GUI.OSD_Components.Widget_VolumeMeter extends GUI.OSD_Components.Gadget
{
   var CH_1;
   var CH_2;
   var CH_3;
   var CH_4;
   var __gpdb;
   var _visible;
   var __show = true;
   function Widget_VolumeMeter()
   {
      super();
      _global.VxDebug("...........................................................................CTOR Widget_VolumeMeter()");
      this.__gpdb = _global.gpdb;
      this.DisplayChannels();
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.RUN_STATE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_1.ENABLE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_2.ENABLE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_3.ENABLE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_4.ENABLE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_1.SOURCE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_2.SOURCE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_3.SOURCE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_4.SOURCE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_1.PHANTOM48V_ENABLE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_2.PHANTOM48V_ENABLE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_3.PHANTOM48V_ENABLE",_loc2_);
      this.__gpdb.addCallback("AUDIO.INPUT.CHANNEL_4.PHANTOM48V_ENABLE",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "GUI.RUN_STATE":
            if(value == "GUI_STATE_3_INITIALIZE_GUI_STATE")
            {
               this.LableAudioGainButtons();
            }
            break;
         case "AUDIO.INPUT.CHANNEL_1.SOURCE":
         case "AUDIO.INPUT.CHANNEL_2.SOURCE":
         case "AUDIO.INPUT.CHANNEL_3.SOURCE":
         case "AUDIO.INPUT.CHANNEL_4.SOURCE":
            this.LableAudioGainButtons();
            this.HandlePhantomPower();
            this.DisplayChannels();
            break;
         case "AUDIO.INPUT.CHANNEL_1.ENABLE":
         case "AUDIO.INPUT.CHANNEL_2.ENABLE":
         case "AUDIO.INPUT.CHANNEL_3.ENABLE":
         case "AUDIO.INPUT.CHANNEL_4.ENABLE":
         case "AUDIO.INPUT.CHANNEL_1.PHANTOM48V_ENABLE":
         case "AUDIO.INPUT.CHANNEL_2.PHANTOM48V_ENABLE":
         case "AUDIO.INPUT.CHANNEL_3.PHANTOM48V_ENABLE":
         case "AUDIO.INPUT.CHANNEL_4.PHANTOM48V_ENABLE":
            this.HandlePhantomPower();
            this.DisplayChannels();
         default:
            return;
      }
   }
   function LableAudioGainButtons()
   {
      var _loc6_;
      var _loc7_;
      var _loc3_ = 1;
      var _loc2_;
      var _loc4_;
      var _loc5_;
      while(_loc3_ <= 4)
      {
         _loc2_ = _loc3_.toString();
         _loc4_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_" + _loc2_ + ".SOURCE") ? "CH " + _loc2_ + " (MIC)" : "CH " + _loc2_ + " (LINE)";
         _loc6_ = GUI.OSD_Components.PanelButtonMC(GUI.OSD_Components.MenuManager.GetManager().GetPanelWidget("Panel_Audio","BUTTON_InputLevel_" + _loc2_));
         _loc6_.SetLabel(_loc4_);
         _loc5_ = "LINE" != this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_" + _loc2_ + ".SOURCE") ? 0 : 1;
         _loc7_ = GUI.OSD_Components.MenuPanelMC(GUI.OSD_Components.MenuManager.GetManager().GetPanel("Panel_Audio_Level_" + _loc2_));
         _loc7_.defaultFocusItem(_loc5_);
         _loc3_ = _loc3_ + 1;
      }
   }
   function HandlePhantomPower()
   {
      var _loc2_ = 1;
      var _loc3_;
      var _loc4_;
      while(_loc2_ <= 4)
      {
         _loc3_ = _loc2_.toString();
         _loc4_ = "AUDIO.INPUT.CHANNEL_" + _loc3_ + ".PHANTOM48V_ENABLE";
         if(!this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_" + _loc3_ + ".ENABLE"))
         {
            this.__gpdb.paramSet(_loc4_,false);
         }
         if("LINE" == this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_" + _loc3_ + ".SOURCE"))
         {
            this.__gpdb.paramSet(_loc4_,false);
         }
         _loc2_ = _loc2_ + 1;
      }
   }
   function DisplayChannels()
   {
      this.CH_1.text = this.ChannelText(1);
      this.CH_2.text = this.ChannelText(2);
      this.CH_3.text = this.ChannelText(3);
      this.CH_4.text = this.ChannelText(4);
      this.ColorText();
   }
   function ChannelText(ch)
   {
      var _loc2_;
      var _loc3_ = ch.toString();
      var _loc4_;
      var _loc5_;
      if(this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_" + _loc3_ + ".ENABLE"))
      {
         _loc4_ = this.__gpdb.paramGet("AUDIO.INPUT.CHANNEL_" + _loc3_ + ".SOURCE");
         _loc5_ = this.__gpdb.paramGetBoolean("AUDIO.INPUT.CHANNEL_" + _loc3_ + ".PHANTOM48V_ENABLE");
         if(_loc5_)
         {
            _loc2_ = "48V";
         }
         else
         {
            switch(_loc4_)
            {
               case "LINE":
                  _loc2_ = "Line";
                  break;
               case "MICROPHONE":
                  _loc2_ = "mic";
                  break;
               default:
                  _loc2_ = "???";
            }
         }
      }
      else
      {
         _loc2_ = "OFF";
      }
      return _loc2_;
   }
   function ColorText()
   {
      var _loc2_;
      _loc2_ = this.CH_1.getTextFormat();
      _loc2_.color = this.CH_1.text != "48V" ? 10066329 : 16776960;
      this.CH_1.setTextFormat(_loc2_);
      _loc2_ = this.CH_2.getTextFormat();
      _loc2_.color = this.CH_2.text != "48V" ? 10066329 : 16776960;
      this.CH_2.setTextFormat(_loc2_);
      _loc2_ = this.CH_3.getTextFormat();
      _loc2_.color = this.CH_3.text != "48V" ? 10066329 : 16776960;
      this.CH_3.setTextFormat(_loc2_);
      _loc2_ = this.CH_4.getTextFormat();
      _loc2_.color = this.CH_4.text != "48V" ? 10066329 : 16776960;
      this.CH_4.setTextFormat(_loc2_);
   }
   function Activate(enable)
   {
      this.__state = !enable ? this.GMODE_HIDE : this.GMODE_RUN;
      _global.VxDebug("Widget_VolumeMeter::Activate(" + enable + ")");
      this._visible = enable;
   }
   function onInputEvent(name, value)
   {
      switch(name)
      {
         case GUI.OSD_Components.TabManager.EVENT_RIGHT:
         case GUI.OSD_Components.TabManager.EVENT_LEFT:
         case GUI.OSD_Components.TabManager.EVENT_UP:
         case GUI.OSD_Components.TabManager.EVENT_DOWN:
         case GUI.OSD_Components.TabManager.EVENT_NE:
         case GUI.OSD_Components.TabManager.EVENT_SE:
         case GUI.OSD_Components.TabManager.EVENT_SW:
         case GUI.OSD_Components.TabManager.EVENT_NW:
         default:
            return;
      }
   }
}

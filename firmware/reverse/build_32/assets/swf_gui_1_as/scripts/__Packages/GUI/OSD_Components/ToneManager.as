class GUI.OSD_Components.ToneManager
{
   var __gpdb;
   var __menuMgr;
   function ToneManager()
   {
      this.__gpdb = _global.gpdb;
      this.__menuMgr = GUI.OSD_Components.MenuManager.GetManager();
      this.AddCallbacks();
   }
   function AddCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.Update);
      this.__gpdb.addCallback("GUI.SOFTKEY.TONAL_RESPONSE.POINT",_loc2_);
      this.__gpdb.addCallback("GUI.SOFTKEY.TONAL_RESPONSE.X",_loc2_);
      this.__gpdb.addCallback("GUI.SOFTKEY.TONAL_RESPONSE.Y",_loc2_);
   }
   function Update(name, value)
   {
      switch(name)
      {
         case "GUI.SOFTKEY.TONAL_RESPONSE.POINT":
            this.UpdateGuiTonePoints(value);
            break;
         case "GUI.SOFTKEY.TONAL_RESPONSE.X":
            this.SetTonePoint("AXIS_X",Number(value));
            break;
         case "GUI.SOFTKEY.TONAL_RESPONSE.Y":
            this.SetTonePoint("AXIS_Y",Number(value));
      }
   }
   function UpdateGuiTonePoints(point)
   {
      var _loc3_ = "NONE";
      var _loc2_ = "NONE";
      var _loc5_ = GUI.OSD_Components.PanelButtonMC(this.__menuMgr.GetPanelWidget("Panel_UserTone","BUTTON_TonalResponse_X"));
      var _loc4_ = GUI.OSD_Components.PanelButtonMC(this.__menuMgr.GetPanelWidget("Panel_UserTone","BUTTON_TonalResponse_Y"));
      switch(point)
      {
         case "TONE_BLACK_POINT":
            _loc5_.SetLabel("BLACK X");
            _loc4_.SetLabel("BLACK Y");
            _loc2_ = "GUI.PAINT.TONE.BLACK_Y";
            _loc3_ = "GUI.PAINT.TONE.BLACK_X";
            break;
         case "TONE_LOW_POINT":
            _loc5_.SetLabel("TOE X");
            _loc4_.SetLabel("TOE Y");
            _loc2_ = "GUI.PAINT.TONE.LOW_Y";
            _loc3_ = "GUI.PAINT.TONE.LOW_X";
            break;
         case "TONE_MID_POINT":
            _loc5_.SetLabel("CENTER X");
            _loc4_.SetLabel("CENTER Y");
            _loc2_ = "GUI.PAINT.TONE.MED_Y";
            _loc3_ = "GUI.PAINT.TONE.MED_X";
            break;
         case "TONE_HIGH_POINT":
            _loc5_.SetLabel("KNEE X");
            _loc4_.SetLabel("KNEE Y");
            _loc2_ = "GUI.PAINT.TONE.HIGH_Y";
            _loc3_ = "GUI.PAINT.TONE.HIGH_X";
            break;
         case "TONE_WHITE_POINT":
            _loc5_.SetLabel("WHITE X");
            _loc4_.SetLabel("WHITE Y");
            _loc2_ = "GUI.PAINT.TONE.WHITE_Y";
            _loc3_ = "GUI.PAINT.TONE.WHITE_X";
      }
      if(_loc2_ != "NONE")
      {
         var _loc7_ = 100 * this.__gpdb.paramGet(_loc2_);
         this.__gpdb.paramSet("GUI.SOFTKEY.TONAL_RESPONSE.Y",_loc7_);
      }
      if(_loc3_ != "NONE")
      {
         var _loc6_ = 100 * this.__gpdb.paramGet(_loc3_);
         this.__gpdb.paramSet("GUI.SOFTKEY.TONAL_RESPONSE.X",_loc6_);
      }
   }
   function SetTonePoint(axis, location)
   {
      var _loc4_ = this.__gpdb.paramGet("GUI.SOFTKEY.TONAL_RESPONSE.POINT");
      var _loc2_ = "NONE";
      switch(_loc4_)
      {
         case "TONE_BLACK_POINT":
            _loc2_ = axis != "AXIS_Y" ? "GUI.PAINT.TONE.BLACK_X" : "GUI.PAINT.TONE.BLACK_Y";
            break;
         case "TONE_LOW_POINT":
            _loc2_ = axis != "AXIS_Y" ? "GUI.PAINT.TONE.LOW_X" : "GUI.PAINT.TONE.LOW_Y";
            break;
         case "TONE_MID_POINT":
            _loc2_ = axis != "AXIS_Y" ? "GUI.PAINT.TONE.MED_X" : "GUI.PAINT.TONE.MED_Y";
            break;
         case "TONE_HIGH_POINT":
            _loc2_ = axis != "AXIS_Y" ? "GUI.PAINT.TONE.HIGH_X" : "GUI.PAINT.TONE.HIGH_Y";
            break;
         case "TONE_WHITE_POINT":
            _loc2_ = axis != "AXIS_Y" ? "GUI.PAINT.TONE.WHITE_X" : "GUI.PAINT.TONE.WHITE_Y";
      }
      if(_loc2_ != "NONE")
      {
         this.__gpdb.paramSet(_loc2_,location / 100);
      }
   }
}

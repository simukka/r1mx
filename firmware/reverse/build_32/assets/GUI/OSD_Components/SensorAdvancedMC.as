class GUI.OSD_Components.SensorAdvancedMC extends GUI.OSD_Components.FullScreenMC
{
   var Deactivate;
   var NewButton;
   var __gpdb;
   static var __sa;
   function SensorAdvancedMC()
   {
      super();
      this.__gpdb = _global.gpdb;
      GUI.OSD_Components.SensorAdvancedMC.__sa = this;
      GUI.OSD_Components.SensorAdvancedMC.__sa._visible = false;
      this.NewButton("Proceed",mx.utils.Delegate.create(this,this.DoProceed),380,540);
      this.NewButton("Abort",mx.utils.Delegate.create(this,this.DoAbort),630,540);
   }
   static function GetManager()
   {
      if(GUI.OSD_Components.SensorAdvancedMC.__sa === undefined)
      {
         _global.VxError("SensorAdvancedMC::GetManager(): ERROR! Called before created.");
      }
      return GUI.OSD_Components.SensorAdvancedMC.__sa;
   }
   function SmartAdvance()
   {
      GUI.OSD_Components.StatusLCD.GetManager().SetMenuTab("Advanced");
      GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_ONESHOT);
      this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","false");
      super.Activate();
   }
   function DoProceed()
   {
      this.cleanup();
      if(this.__gpdb.paramGetBoolean("GUI.ADVANCED.SENSOR_OPTION"))
      {
         this.__gpdb.paramSet("GUI.ADVANCED.SENSOR_OPTION","false");
      }
      else
      {
         this.__gpdb.paramSet("GUI.ADVANCED.SENSOR_OPTION","true");
      }
      GUI.OSD_Components.MenuManager.GetManager().GotoMenuPanel("Panel_BlkShading");
   }
   function DoAbort()
   {
      this.cleanup();
   }
   function cleanup()
   {
      GUI.OSD_Components.StatusLCD.GetManager().SetPane(GUI.OSD_Components.StatusLCD.PANE_STATUS);
      var _loc2_ = this.__gpdb.paramGetNumber("CAMERA.SLAVE_MODE_ACTIVE");
      if(_loc2_ == 0 || _loc2_ == 1)
      {
         this.__gpdb.paramSet("GUI.BUTTON_INPUT_ENABLED","true");
      }
      this.Deactivate(true);
   }
}

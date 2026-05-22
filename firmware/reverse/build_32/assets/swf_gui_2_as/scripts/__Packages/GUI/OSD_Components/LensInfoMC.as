class GUI.OSD_Components.LensInfoMC extends MovieClip
{
   var __gpdb;
   function LensInfoMC(parent, depth)
   {
      super();
      this.__gpdb = _global.gpdb;
      var _loc4_ = this.__gpdb.paramGet("SYSTEM.DEV.TTY0.ASSIGNMENT");
      this.__gpdb.paramSet("GUI.SOFTKEY.S4I_LENS_PORT_ACTIVE",_loc4_);
      this.SmartEnable();
      this.addCallbacks();
   }
   function addCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.update);
      this.__gpdb.addCallback("GUI.OSD.SHOW.LENS_DATA",_loc2_);
      this.__gpdb.addCallback("SYSTEM.DEV.LENS.GIVES_FEEDBACK",_loc2_);
      this.__gpdb.addCallback("VIDEO.MONITOR.TEST_PATTERN.ENABLED",_loc2_);
      this.__gpdb.addCallback("VIDEO.PLAYBACK.STATE",_loc2_);
      this.__gpdb.addCallback("GUI.SOFTKEY.S4I_LENS_PORT_ACTIVE",_loc2_);
   }
   function update(name, value)
   {
      switch(name)
      {
         case "GUI.OSD.SHOW.LENS_DATA":
         case "SYSTEM.DEV.LENS.GIVES_FEEDBACK":
         case "VIDEO.MONITOR.TEST_PATTERN.ENABLED":
         case "VIDEO.PLAYBACK.STATE":
            this.SmartEnable();
            break;
         case "GUI.SOFTKEY.S4I_LENS_PORT_ACTIVE":
            this.Manage4SiPort(value);
      }
   }
   function Manage4SiPort(value)
   {
      this.__gpdb.paramSet("SYSTEM.DEV.TTY0.ASSIGNMENT",value);
   }
   function SmartEnable()
   {
      var _loc5_ = this.__gpdb.paramGetBoolean("GUI.OSD.SHOW.LENS_DATA");
      var _loc3_ = this.__gpdb.paramGetBoolean("SYSTEM.DEV.LENS.GIVES_FEEDBACK");
      var _loc6_ = this.__gpdb.paramGetBoolean("VIDEO.MONITOR.TEST_PATTERN.ENABLED");
      var _loc4_ = "IDLE" != this.__gpdb.paramGet("VIDEO.PLAYBACK.STATE");
      var _loc2_ = _loc5_ && _loc3_ && !_loc6_ && !_loc4_;
      this.Show(_loc2_);
   }
   function Show(show)
   {
      this._visible = show;
   }
}

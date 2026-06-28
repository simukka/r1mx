class GUI.OSD_Components.Widget_SDCard extends MovieClip
{
   var __gpdb;
   var __sdPath;
   var __sdPresent;
   function Widget_SDCard()
   {
      super();
      this.__gpdb = _global.gpdb;
      this.__sdPath = this.__gpdb.paramGet("SYSTEM.DEV.SDCARD.ROOT_PATH");
      this.__sdPresent = this.__sdPath.length > 0;
      this.HandleInsert(this.__sdPresent);
      this.addCallbacks();
      this._visible = this.__sdPresent;
   }
   function HandleInsert(present)
   {
      var _loc2_ = !present ? "" : this.__sdPath + "/PROFILES";
      this._visible = present;
      this.__gpdb.paramSet("SYSTEM.PROFILE.FILE_LIST.SEARCH_DIRECTORY",_loc2_);
   }
   function addCallbacks()
   {
      var _loc2_ = mx.utils.Delegate.create(this,this.update);
      this.__gpdb.addCallback("SYSTEM.DEV.SDCARD.ROOT_PATH",_loc2_);
   }
   function update(name, value)
   {
      var _loc0_;
      if((_loc0_ = name) === "SYSTEM.DEV.SDCARD.ROOT_PATH")
      {
         this.__sdPath = value;
         this.__sdPresent = value.length > 0;
         this.HandleInsert(this.__sdPresent);
      }
   }
}

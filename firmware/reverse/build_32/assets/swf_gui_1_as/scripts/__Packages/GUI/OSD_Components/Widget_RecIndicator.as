class GUI.OSD_Components.Widget_RecIndicator extends MovieClip
{
   var __gpdb;
   function Widget_RecIndicator()
   {
      super();
      this.__gpdb = _global.gpdb;
      this._visible = false;
      this.AddCallbacks();
   }
   function Paint(state)
   {
      switch(state)
      {
         case "ACTIVE":
            this.gotoAndStop("FRAME_RECORD");
            this._visible = true;
            break;
         case "PRERECORD":
            this.gotoAndStop("FRAME_PRERECORD");
            this._visible = true;
            break;
         default:
            this._visible = false;
      }
   }
   function AddCallbacks()
   {
      this.__gpdb.addCallback("VIDEO.RECORD.STATE",mx.utils.Delegate.create(this,this.HandleCB));
   }
   function HandleCB(name, value)
   {
      var _loc0_ = null;
      if((_loc0_ = name) === "VIDEO.RECORD.STATE")
      {
         this.Paint(value);
      }
   }
}

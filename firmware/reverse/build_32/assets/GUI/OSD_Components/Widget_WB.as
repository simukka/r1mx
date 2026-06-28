class GUI.OSD_Components.Widget_WB
{
   var __WB;
   var __degreeSymbol;
   var __gpdb;
   function Widget_WB()
   {
      this.__gpdb = _global.gpdb;
      this.setWB(this.__gpdb.paramGet("PAINT.WHITE_BALANCE.CURRENT"));
      this.addCallbacks();
   }
   function setWB(value)
   {
      this.__WB.text = value;
      var _loc2_ = this.__WB.getTextFormat();
      var _loc3_ = _loc2_.getTextExtent(value).width;
      this.__degreeSymbol._x = this.__WB._x + _loc3_;
   }
   function addCallbacks()
   {
      this.__gpdb.addCallback("PAINT.WHITE_BALANCE.CURRENT",mx.utils.Delegate.create(this,this.update));
   }
   function update(name, value)
   {
      var _loc0_;
      if((_loc0_ = name) === "PAINT.WHITE_BALANCE.CURRENT")
      {
         this.setWB(value);
      }
   }
}

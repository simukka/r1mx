class GUI.OSD_Components.PositionIndicatorMC extends MovieClip
{
   var __numElements;
   var __index;
   var __markerIndex;
   function PositionIndicatorMC()
   {
      super();
      this.__numElements = 0;
      this.__index = 0;
      this.__markerIndex = null;
   }
   function SetLength(length)
   {
      this.__numElements = length;
   }
   function SetIndex(index)
   {
      this.__index = !index ? 0 : index;
   }
   function SetMarkerIndex(index)
   {
      this.__markerIndex = !index ? 0 : index;
      this.Paint();
   }
   function Paint()
   {
   }
}

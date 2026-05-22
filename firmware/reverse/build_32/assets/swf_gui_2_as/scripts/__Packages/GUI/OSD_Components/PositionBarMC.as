class GUI.OSD_Components.PositionBarMC extends GUI.OSD_Components.PositionIndicatorMC
{
   var __bar;
   var __width;
   var __sliderWidth;
   var __slider;
   var __marker;
   var __numElements;
   var __index;
   var __markerIndex;
   static var BAR_SYMBOL = "PositionBar";
   static var SLIDER_SYMBOL = "PositionSlider";
   static var MARKER_SYMBOL = "PositionMarker";
   function PositionBarMC()
   {
      super();
      this.createEmptyMovieClip("__bar",this.getNextHighestDepth());
      var _loc3_ = 0;
      this.__bar.attachMovie(GUI.OSD_Components.PositionBarMC.BAR_SYMBOL + "Left","leftCap",this.__bar.getNextHighestDepth(),{_x:_loc3_});
      var _loc5_ = _loc3_ + this.__bar.leftCap._width;
      this.__bar.attachMovie(GUI.OSD_Components.PositionBarMC.BAR_SYMBOL + "Center","centerCap",this.__bar.getNextHighestDepth(),{_x:_loc5_});
      var _loc8_ = this.__bar.centerCap._width;
      this.__bar.attachMovie(GUI.OSD_Components.PositionBarMC.BAR_SYMBOL + "Right","rightCap",this.__bar.getNextHighestDepth());
      var _loc4_ = this.__width - this.__bar.rightCap._width;
      this.__bar.rightCap._x = _loc4_;
      this.__bar.centerCap._width = _loc4_ - _loc5_;
      this.__sliderWidth = _loc4_ + this.__bar.rightCap._width;
      this.createEmptyMovieClip("__slider",this.getNextHighestDepth());
      _loc3_ = 0;
      this.__slider.attachMovie(GUI.OSD_Components.PositionBarMC.SLIDER_SYMBOL + "Left","leftCap",this.__slider.getNextHighestDepth(),{_x:_loc3_});
      _loc5_ = _loc3_ + this.__slider.leftCap._width;
      this.__slider.attachMovie(GUI.OSD_Components.PositionBarMC.SLIDER_SYMBOL + "Center","centerCap",this.__slider.getNextHighestDepth(),{_x:_loc5_});
      _loc4_ = _loc5_ + this.__slider.centerCap._width;
      this.__slider.centerCap.minWidth = this.__slider.centerCap._width;
      this.__slider.attachMovie(GUI.OSD_Components.PositionBarMC.SLIDER_SYMBOL + "Right","rightCap",this.__slider.getNextHighestDepth(),{_x:_loc4_});
      this.createEmptyMovieClip("__marker",this.getNextHighestDepth());
      _loc3_ = this.__slider.centerCap._x;
      this.__marker.attachMovie(GUI.OSD_Components.PositionBarMC.MARKER_SYMBOL + "Center","centerCap",this.__marker.getNextHighestDepth(),{_x:_loc3_});
      this.__marker.attachMovie(GUI.OSD_Components.PositionBarMC.MARKER_SYMBOL + "CenterMatch","centerCapMatch",this.__marker.getNextHighestDepth(),{_x:_loc3_,_visible:false});
      this.__marker.swapDepths(this.__slider);
   }
   function SetLength(length)
   {
      super.SetLength(length);
      if(length == 0)
      {
         this.__slider._visible = false;
      }
      else
      {
         this.__slider._visible = true;
         this.expandSlider();
      }
   }
   function expandSlider()
   {
      var _loc3_ = this.__slider.leftCap._width;
      var _loc4_ = this.__slider.rightCap._width;
      var _loc2_ = Math.floor(this.__sliderWidth / this.__numElements - _loc3_ - _loc4_);
      if(_loc2_ < this.__slider.centerCap.minWidth)
      {
         _loc2_ = this.__slider.centerCap.minWidth;
      }
      this.__slider.centerCap._width = _loc2_;
      this.__slider.rightCap._x = this.__slider.centerCap._x + _loc2_;
      this.__marker.centerCap._width = _loc2_;
      this.__marker.centerCapMatch._width = _loc2_;
      paint();
   }
   function Paint()
   {
      var _loc5_ = this.__slider.leftCap._width;
      var _loc7_ = this.__slider.rightCap._width;
      var _loc6_ = this.__slider.centerCap._width;
      var _loc2_ = 0;
      this.ReconcileSettings();
      if(this.__numElements > 1)
      {
         _loc2_ = (this.__sliderWidth - _loc5_ - _loc7_ - _loc6_) / (this.__numElements - 1);
      }
      var _loc3_ = _loc2_ * this.__index;
      this.__slider._x = Math.floor(_loc3_);
      _loc3_ = _loc2_ * this.__markerIndex;
      var _loc4_ = this.__markerIndex == this.__index;
      this.__marker._x = Math.floor(_loc3_);
      this.__marker._visible = this.__markerIndex !== null;
      this.__marker.centerCap._visible = !_loc4_;
      this.__marker.centerCapMatch._visible = _loc4_;
   }
   function ReconcileSettings()
   {
      return undefined;
   }
}

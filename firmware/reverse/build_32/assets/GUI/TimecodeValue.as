class GUI.TimecodeValue
{
   var __dropFrame;
   var __ff;
   var __hh;
   var __interlaced;
   var __mm;
   var __prefix;
   var __rate;
   var __ss;
   function TimecodeValue(tc, rate, dropFrame, interlaced, prefix)
   {
      this.SetRate(rate);
      this.SetDropFrame(Boolean(dropFrame));
      this.SetInterlaced(Boolean(interlaced));
      this.SetStringValue(tc);
      if(prefix == undefined || prefix == null)
      {
         prefix = "";
      }
      this.__prefix = String(prefix);
   }
   function GetString(withPrefix)
   {
      var _loc3_ = !this.__dropFrame ? ":" : ";";
      var _loc2_ = this.__ff;
      if(this.__interlaced || this.__rate > 30)
      {
         if(!(_loc2_ & 1))
         {
            _loc3_ = !this.__dropFrame ? "." : ",";
         }
         _loc2_ = Math.floor(_loc2_ / 2);
      }
      var _loc7_ = this.__hh >= 10 ? this.__hh.toString() : "0" + this.__hh.toString();
      var _loc5_ = this.__mm >= 10 ? this.__mm.toString() : "0" + this.__mm.toString();
      var _loc6_ = this.__ss >= 10 ? this.__ss.toString() : "0" + this.__ss.toString();
      var _loc4_ = _loc2_ >= 10 ? _loc2_.toString() : "0" + _loc2_.toString();
      return (!(withPrefix && this.__prefix != "") ? "" : this.__prefix + " ") + _loc7_ + _loc3_ + _loc5_ + _loc3_ + _loc6_ + _loc3_ + _loc4_;
   }
   function SetInterlaced(interlaced)
   {
      this.__interlaced = interlaced;
   }
   function SetDropFrame(dropFrame)
   {
      this.__dropFrame = dropFrame;
   }
   function SetRate(rate)
   {
      this.__rate = Math.ceil(rate);
   }
   function GetRate()
   {
      return this.__rate;
   }
   function SetStringValue(timecode)
   {
      this.__hh = parseInt(timecode.substr(0,2));
      this.__mm = parseInt(timecode.substr(3,2));
      this.__ss = parseInt(timecode.substr(6,2));
      this.__ff = parseInt(timecode.substr(9,2));
      if(isNaN(this.__hh))
      {
         this.__hh = 0;
      }
      if(isNaN(this.__mm))
      {
         this.__mm = 0;
      }
      if(isNaN(this.__ss))
      {
         this.__ss = 0;
      }
      if(isNaN(this.__ff))
      {
         this.__ff = 0;
      }
      var _loc3_ = timecode.substr(8,1);
      if(this.__interlaced || this.__rate > 30)
      {
         this.__ff *= 2;
         if(_loc3_ == ":" || _loc3_ == ";")
         {
            this.__ff = this.__ff + 1;
         }
      }
   }
   function SetFrames(frames)
   {
      this.SetParts(0,0,0,0);
      this.Advance(frames);
   }
   function SetParts(hh, mm, ss, ff)
   {
      this.__hh = hh;
      this.__mm = mm;
      this.__ss = ss;
      this.__ff = ff;
   }
   function SetPrefix(prefix)
   {
      this.__prefix = prefix;
   }
   function Advance(frames)
   {
      if(frames == 0)
      {
         return undefined;
      }
      var _loc3_;
      var _loc6_;
      var _loc4_;
      var _loc5_;
      var _loc7_;
      var _loc2_;
      if(this.__dropFrame)
      {
         _loc3_ = 0;
         if(this.__rate == 60)
         {
            _loc3_ = 4;
         }
         else if(this.__rate == 30)
         {
            _loc3_ = 2;
         }
         _loc6_ = 60 * this.__rate;
         _loc4_ = _loc6_ - _loc3_;
         _loc5_ = 10 * _loc4_ + _loc3_;
         _loc7_ = 6 * _loc5_;
         _loc2_ = this.GetFramesSinceZero() + frames;
         if(_loc2_ < 0)
         {
            _loc2_ = 0;
         }
         _loc2_ = Math.floor(_loc2_ / _loc7_);
         this.__hh = _loc2_ % 24;
         _loc2_ %= _loc7_;
         this.__mm = 10 * Math.floor(_loc2_ / _loc5_);
         _loc2_ %= _loc5_;
         if(_loc2_ >= _loc6_)
         {
            this.__mm += 1;
            _loc2_ -= _loc6_;
            this.__mm += Math.floor(_loc2_ / _loc4_);
            _loc2_ %= _loc4_;
            this.__ss = Math.floor((_loc2_ + _loc3_) / this.__rate);
            this.__ff = (_loc2_ + _loc3_) % this.__rate;
         }
         else
         {
            this.__ss = Math.floor(_loc2_ / this.__rate);
            this.__ff = _loc2_ % this.__rate;
         }
      }
      else
      {
         _loc2_ = this.GetFramesSinceZero() + frames;
         if(_loc2_ < 0)
         {
            _loc2_ = 0;
         }
         this.__hh = Math.floor(_loc2_ / (this.__rate * 3600)) % 24;
         _loc2_ %= this.__rate * 3600;
         this.__mm = Math.floor(_loc2_ / (this.__rate * 60));
         _loc2_ %= this.__rate * 60;
         this.__ss = Math.floor(_loc2_ / this.__rate);
         this.__ff = _loc2_ % this.__rate;
      }
   }
   function AdvanceMS(ms, factor)
   {
      if(factor === undefined)
      {
         factor = 1;
      }
      var _loc2_ = ms * factor;
      var _loc6_ = false;
      if(_loc2_ < 0)
      {
         _loc6_ = true;
         _loc2_ = - _loc2_;
      }
      var _loc4_ = Math.floor(this.__rate * _loc2_ / 1000);
      if(_loc6_)
      {
         this.Advance(- _loc4_);
      }
      else
      {
         this.Advance(_loc4_);
      }
      var _loc3_ = _loc2_ - _loc4_ / this.__rate * 1000;
      if(factor != 0)
      {
         _loc3_ /= factor;
         if(_loc3_ < 0)
         {
            _loc3_ = - _loc3_;
         }
      }
      return _loc3_;
   }
   function GetFramesSinceZero()
   {
      var _loc2_ = this.__ff + this.__rate * (this.__ss + this.__mm * 60 + this.__hh * 3600);
      var _loc3_;
      var _loc4_;
      var _loc5_;
      var _loc6_;
      if(this.__dropFrame)
      {
         _loc3_ = 0;
         if(this.__rate == 60)
         {
            _loc3_ = 4;
         }
         else if(this.__rate == 30)
         {
            _loc3_ = 2;
         }
         _loc4_ = _loc3_;
         _loc5_ = 9 * _loc4_;
         _loc6_ = 6 * _loc5_;
         _loc2_ -= _loc6_ * this.__hh;
         _loc2_ -= _loc5_ * Math.floor(this.__mm / 10);
         _loc2_ -= _loc4_ * this.__mm % 10;
      }
      return _loc2_;
   }
   function GetMS()
   {
      return this.GetFramesSinceZero() * 1000 / this.__rate;
   }
}

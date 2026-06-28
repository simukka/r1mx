class GUI.OSD_Components.GizmoGrid
{
   var __isFocused;
   var __list;
   var __x;
   var __y;
   function GizmoGrid(list, x, y, focused)
   {
      this.__list = list !== undefined ? list : new Array(new Array(null));
      if(this.__list.length == 0 || !(this.__list[0] instanceof Array))
      {
         this.__list = new Array(this.__list);
      }
      this.__y = y !== undefined ? y : 0;
      if(this.__y >= this.__list.length)
      {
         this.__y = 0;
      }
      this.__x = x !== undefined ? x : 0;
      if(this.__x >= this.__list[this.__y].length)
      {
         this.__x = 0;
      }
      this.__isFocused = focused !== undefined ? focused : true;
   }
   function SetFocused(focused)
   {
      this.__isFocused = focused;
   }
   function setVisible(visible)
   {
      var _loc3_ = 0;
      var _loc2_;
      while(_loc3_ < this.__list.length)
      {
         _loc2_ = 0;
         while(_loc2_ < this.__list[_loc3_].length)
         {
            this.__list[_loc3_][_loc2_]._visible = visible;
            _loc2_ = _loc2_ + 1;
         }
         _loc3_ = _loc3_ + 1;
      }
   }
   function isFocused()
   {
      return this.__isFocused;
   }
   function current()
   {
      return this.__list[this.__y][this.__x];
   }
   function next()
   {
      if(!this.__isFocused)
      {
         return this.current();
      }
      var _loc3_ = this.__x;
      var _loc2_ = this.__y;
      do
      {
         this.__x = this.__x + 1;
         if(this.__x >= this.__list[this.__y].length)
         {
            this.__x = 0;
            this.__y = this.__y + 1;
            if(this.__y >= this.__list.length)
            {
               this.__y = 0;
            }
         }
      }
      while(this.__list[this.__y][this.__x] === null && (this.__x != _loc3_ || this.__y != _loc2_));
      return this.__list[this.__y][this.__x];
   }
   function prev()
   {
      if(!this.__isFocused)
      {
         return this.current();
      }
      var _loc3_ = this.__x;
      var _loc2_ = this.__y;
      do
      {
         this.__x = this.__x - 1;
         if(this.__x < 0)
         {
            this.__y = this.__y - 1;
            if(this.__y < 0)
            {
               this.__y = this.__list.length - 1;
            }
            this.__x = this.__list[this.__y].length - 1;
         }
      }
      while(this.__list[this.__y][this.__x] === null && this.__x != _loc3_ && this.__y != _loc2_);
      return this.__list[this.__y][this.__x];
   }
   function HasPrev()
   {
      return this.__x != 0;
   }
   function HasNext()
   {
      return this.__x < this.__list[this.__y].length - 1;
   }
   function HasUp()
   {
      return this.__y != 0;
   }
   function HasDown()
   {
      return this.__y < this.__list.length - 1;
   }
   function left()
   {
      if(!this.__isFocused || !this.HasPrev())
      {
         return this.current();
      }
      var _loc2_ = this.__x;
      this.__x = this.__x - 1;
      while(this.__x > 0 && this.__list[this.__y][this.__x] === null)
      {
         this.__x = this.__x - 1;
      }
      if(this.__list[this.__y][this.__x] === null)
      {
         this.__x = _loc2_;
      }
      return this.__list[this.__y][this.__x];
   }
   function right()
   {
      if(!this.__isFocused || !this.HasNext())
      {
         return this.current();
      }
      var _loc2_ = this.__x;
      this.__x = this.__x + 1;
      while(this.__x < this.__list[this.__y].length - 1 && this.__list[this.__y][this.__x] === null)
      {
         this.__x = this.__x + 1;
      }
      if(this.__list[this.__y][this.__x] === null)
      {
         this.__x = _loc2_;
      }
      return this.__list[this.__y][this.__x];
   }
   function up()
   {
      if(!this.__isFocused || !this.HasUp())
      {
         return this.current();
      }
      var _loc2_ = this.__x;
      this.__y = this.__y - 1;
      while(this.__list[this.__y][this.__x] === null && this.__x > 0)
      {
         this.__x = this.__x - 1;
      }
      if(this.__list[this.__y][this.__x] === null)
      {
         this.__x = _loc2_ + 1;
         while(this.__list[this.__y][this.__x] === null && this.__x < this.__list[this.__y].length - 1)
         {
            this.__x = this.__x + 1;
         }
      }
      return this.__list[this.__y][this.__x];
   }
   function down()
   {
      if(!this.__isFocused || !this.HasDown())
      {
         return this.current();
      }
      var _loc2_ = this.__x;
      this.__y = this.__y + 1;
      while(this.__list[this.__y][this.__x] === null && this.__x > 0)
      {
         this.__x = this.__x - 1;
      }
      if(this.__list[this.__y][this.__x] === null)
      {
         this.__x = _loc2_ + 1;
         while(this.__list[this.__y][this.__x] === null && this.__x < this.__list[this.__y].length - 1)
         {
            this.__x = this.__x + 1;
         }
      }
      return this.__list[this.__y][this.__x];
   }
}

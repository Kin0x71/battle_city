from defines import *

class map_navigation:
    map_w=0
    map_h=0
    map_rows=0
    map_cells=0
    astar_rows=0
    astar_cells=0
    astar_map=None
    collide_list=None

    def fill(self,maze):
        self.map_rows=len(maze)
        self.map_cells=len(maze[0])

        self.astar_rows=self.map_rows-1
        self.astar_cells=self.map_cells-1

        self.map_w = self.map_cells*BLOCK_SIZE
        self.map_h = self.map_rows*BLOCK_SIZE

        self.map_src=[]
        for yi in range(0, self.map_rows):
            row = []
            for xi in range(0, self.map_cells):
                row.append(maze[yi][xi])
            self.map_src.append(row)

        self.astar_map = []
        for yi in range(0, self.astar_rows):
            row = []
            for xi in range(0, self.astar_cells):
                row.append(0)
            self.astar_map.append(row)

        for ri in range(1, self.map_rows-1):
            for ci in range(1, self.map_cells-1):
                if self.map_src[ri][ci]==0:
                    self.astar_map[ri][ci]=0
                else:
                    if self.map_src[ri][ci]>0:
                        self.astar_map[ri][ci]=1
                        self.astar_map[ri-1][ci]=1
                        self.astar_map[ri][ci-1]=1
                        self.astar_map[ri-1][ci-1]=1
                    else:
                        self.astar_map[ri][ci]=0

        for ri in range(1, self.map_rows-1):
            if self.map_src[ri][0]>0:
                self.astar_map[ri][0]=1
                self.astar_map[ri-1][0]=1

            if self.map_src[ri][self.map_cells-1]>0:
                self.astar_map[ri][self.astar_cells-1]=1
                self.astar_map[ri-1][self.astar_cells-1]=1

        for ci in range(1, self.map_cells-1):
            if self.map_src[0][ci]>0:
                self.astar_map[0][ci]=1
                self.astar_map[0][ci-1]=1

            if self.map_src[self.map_rows-1][ci]>0:
                self.astar_map[self.astar_rows-1][ci]=1
                self.astar_map[self.astar_rows-1][ci-1]=1

        if self.map_src[0][0]>0:
            self.astar_map[0][0]=1

        if self.map_src[0][self.map_rows-1]>0:
            self.astar_map[0][self.astar_cells-1]=1

        if self.map_src[self.map_rows-1][self.map_cells-1]>0:
            self.astar_map[self.astar_rows-1][self.astar_cells-1]=1

        if self.map_src[self.map_rows-1][0]>0:
            self.astar_map[self.astar_rows-1][0]=1

        self.rebuild_colliders()

    def remove_cell_by_position(self, world_x, world_y):
        mr = int(world_y/BLOCK_SIZE)
        mc = int(world_x/BLOCK_SIZE)

        self.map_src[mr][mc] = 0

        amr=min(mr-1,0)
        amc=min(mc-1,0)
        bmr=min(mr+1,self.map_rows-1)
        bmc=min(mc+1,self.map_cells-1)

        for imr in range(amr, bmr):
            for imc in range(amc, bmc):
                if self.map_src[imr][imc] < 1 and self.map_src[imr+1][imc] < 1 and self.map_src[imr][imc+1] < 1 and self.map_src[imr+1][imc+1] < 1:
                    self.astar_map[imr][imc] = 0

        self.rebuild_colliders()
    
    def rebuild_colliders(self):
        
        line_t=[]
        line_b=[]
        lines_top=[]
        lines_bottom=[]
        
        for ri in range(0, self.map_rows):
            for ci in range(0, self.map_cells):
                if self.map_src[ri][ci] > 0:

                    if ri>0:
                        if self.map_src[ri-1][ci] < 1:
                            if len(line_t)==0:
                                line_t.append((ci-1,ri-1))
                            line_t.append((ci,ri-1))
                    else:
                        if len(line_t)==0:
                            line_t.append((ci-1,ri-1))
                        line_t.append((ci,ri-1))

                    if ri<self.map_rows-1:
                        if self.map_src[ri+1][ci] < 1:
                            if len(line_b)==0:
                                line_b.append((ci-1,ri))
                            line_b.append((ci,ri))
                    else:
                        if len(line_b)==0:
                            line_b.append((ci-1,ri))
                        line_b.append((ci,ri))
                else:

                    if len(line_t)>0:
                        lines_top.append(line_t)
                    if len(line_b)>0:
                        lines_bottom.append(line_b)
                    line_t=[]
                    line_b=[]

            if len(line_t)>0:
                lines_top.append(line_t)
            if len(line_b)>0:
                lines_bottom.append(line_b)
            line_t=[]
            line_b=[]

        if len(line_t)>0:
            lines_top.append(line_t)
        if len(line_b)>0:
            lines_bottom.append(line_b)

        #========================================================

        line_l=[]
        line_r=[]
        lines_left=[]
        lines_right=[]
        for ci in range(0, self.map_cells):
            for ri in range(0, self.map_rows):
                if self.map_src[ri][ci] > 0:
                    if self.map_src[ri][ci-1] < 1:
                        if len(line_l)==0:
                            line_l.append((ci-1,ri-1))
                        line_l.append((ci-1,ri))
                    
                    if ci<self.map_cells-1:
                        if self.map_src[ri][ci+1] < 1:
                            if len(line_r)==0:
                                line_r.append((ci,ri-1))
                            line_r.append((ci,ri))
                    else:
                        if len(line_r)==0:
                            line_r.append((ci,ri-1))
                        line_r.append((ci,ri))

                else:

                    if len(line_l)>0:
                        lines_left.append(line_l)
                    if len(line_r)>0:
                        lines_right.append(line_r)
                    line_l=[]
                    line_r=[]

            if len(line_l)>0:
                lines_left.append(line_l)
            if len(line_r)>0:
                lines_right.append(line_r)
            line_l=[]
            line_r=[]

        if len(line_l)>0:
            lines_left.append(line_l)
        if len(line_r)>0:
            lines_right.append(line_r)

        self.collide_list=[]

        for l in lines_top:
            wp=(
                ((l[0][0]*BLOCK_SIZE)+BLOCK_SIZE,(l[0][1]*BLOCK_SIZE)+BLOCK_SIZE),
                ((l[len(l)-1][0]*BLOCK_SIZE)+BLOCK_SIZE,(l[len(l)-1][1]*BLOCK_SIZE)+BLOCK_SIZE)
            )
            self.collide_list.append(wp)

        for l in lines_left:
            wp=(
                ((l[0][0]*BLOCK_SIZE)+BLOCK_SIZE,(l[0][1]*BLOCK_SIZE)+BLOCK_SIZE),
                ((l[len(l)-1][0]*BLOCK_SIZE)+BLOCK_SIZE,(l[len(l)-1][1]*BLOCK_SIZE)+BLOCK_SIZE)
            )
            self.collide_list.append(wp)

        for l in lines_right:
            wp=(
                ((l[0][0]*BLOCK_SIZE)+BLOCK_SIZE,(l[0][1]*BLOCK_SIZE)+BLOCK_SIZE),
                ((l[len(l)-1][0]*BLOCK_SIZE)+BLOCK_SIZE,(l[len(l)-1][1]*BLOCK_SIZE)+BLOCK_SIZE)
            )
            self.collide_list.append(wp)

        for l in lines_bottom:
            wp=(
                ((l[0][0]*BLOCK_SIZE)+BLOCK_SIZE,(l[0][1]*BLOCK_SIZE)+BLOCK_SIZE),
                ((l[len(l)-1][0]*BLOCK_SIZE)+BLOCK_SIZE,(l[len(l)-1][1]*BLOCK_SIZE)+BLOCK_SIZE)
            )
            self.collide_list.append(wp)
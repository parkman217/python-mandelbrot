import pygame, sys, cmath, time, math


def get_mandlebrot(x, y):
    num = complex(x, y)
    curr_num = complex(0, 0)
    max_iter = 100
    for a in range(max_iter):
        curr_num = (curr_num * curr_num) + num
        r, phi = cmath.polar(curr_num)
        if r > 2:
            return a/max_iter
    return 1

def blend_colors(first, second, percent):
    return [first[a]*(1-percent) + second[a]*percent for a in range(len(first))]


def draw_screen(screen, bot_left, top_right, screen_width, divisions, curr_div_loc):
    #bot_left and top_right are coords in space to draw the set
    #curr_div_lock is x, y coords in grid to split in half and draw (zero indexed)
    boxes = 2**(divisions)
    brot_coord_width = top_right[0] - bot_left[0]
    brot_coords_x = brot_coord_width*(curr_div_loc[0])/boxes+bot_left[0]#bot left of the box

    brot_coord_height = top_right[1] - bot_left[1]
    brot_coords_y = brot_coord_height*(curr_div_loc[1])/boxes+bot_left[1]#bot left of the box

    brot = get_mandlebrot(brot_coords_x, brot_coords_y)#middle of the box

    colors = [(0, 0, 0), (0, 0, 255), (0, 255, 255), (255, 255, 255)]#cold to hot
    
    if brot == 1:
        color = (0, 0, 0)
    else:
        color_pair_indices = len(colors)-2#-1 for index -1 for needing to be pairs
        percentage = (brot)**0.5
        first_idx = math.floor(percentage*color_pair_indices)
        percent_gradient = percentage*color_pair_indices-first_idx

        color = blend_colors(colors[first_idx], colors[first_idx+1], percent_gradient)            
        
    if boxes == screen_width:
        screen.set_at((curr_div_loc[0], curr_div_loc[1]), color)
    else:
        rect_width = math.ceil(screen_width / boxes)
        top_left = math.ceil(screen_width*(curr_div_loc[0])/boxes), math.ceil(screen_width*(curr_div_loc[1])/boxes)
        rect = pygame.Rect((top_left), (rect_width, rect_width))
        pygame.draw.rect(screen, color, rect)


def draw_next(screen, bot_left, top_right, screen_width, divisions, curr_div_loc):
    draw_screen(screen, bot_left, top_right, screen_width, divisions, curr_div_loc)
    boxes = 2**(divisions)
    if curr_div_loc[0] == boxes:#looping over to lower
        if curr_div_loc[1] == boxes:#start over with smaller div
            if boxes == screen_width:#done zooming in
                return False, False
            else:
                return (0, 0), divisions+1#position and divisions
        else:
            return (0, curr_div_loc[1]+1), divisions#incrementing the y val
    else:
        return (curr_div_loc[0]+1, curr_div_loc[1]), divisions#incrementing the x val



def run():
    pygame.init()
    screen_size = 512#must be a power of 2
    screen = pygame.display.set_mode((screen_size, screen_size), 0, 32)
    surf = pygame.Surface((screen_size, screen_size))#surface to hold the values
    running = True

    divisions = 0
    curr_pos = (0, 0)
    
    desired_fps = 5
    latency = 1/float(desired_fps)

    brot_xs = [-2, 2]
    brot_ys = [-2, 2]

    last_frame_time = time.time()
    zoom_percent = 0.5#[0, 1] lower the faster
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                old_size = (brot_xs[1] - brot_xs[0], brot_ys[1] - brot_ys[0])#width, height
                reduction_amounts = (old_size[0]*(1-zoom_percent), old_size[1]*(1-zoom_percent))
                percent_pos = (pos[0]/screen_size, pos[1]/screen_size)
                if event.button == 1:
                    brot_xs[0]+=reduction_amounts[0]*percent_pos[0]
                    brot_xs[1]-=reduction_amounts[0]*(1-percent_pos[0])

                    brot_ys[0]+=reduction_amounts[1]*percent_pos[1]
                    brot_ys[1]-=reduction_amounts[1]*(1-percent_pos[1])
                    curr_pos = (0, 0)#reset drawing
                    divisions = 0

                elif event.button == 3:
                    brot_xs[0]-=(reduction_amounts[0])*percent_pos[0]
                    brot_xs[1]+=(reduction_amounts[0])*(1-percent_pos[0])

                    brot_ys[0]-=(reduction_amounts[1])*percent_pos[1]
                    brot_ys[1]+=(reduction_amounts[1])*(1-percent_pos[1])
                    curr_pos = (0, 0)#reset drawing
                    divisions = 0

        last_frame_time = time.time()#reset the last frame time because bout to draw a frame
        while curr_pos != False and time.time() - last_frame_time < latency:
            curr_pos, divisions = draw_next(surf, (brot_xs[0], brot_ys[0]), (brot_xs[1], brot_ys[1]), screen_size, divisions, curr_pos)

        
        screen.blit(surf, (0, 0))
        pygame.display.update()

    pygame.quit()
    sys.exit()



if __name__ == '__main__':
    run()

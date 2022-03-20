import numpy as np
import random
import matplotlib.pyplot as plt
import sys

class GameOfLife(object):
    def __init__(self, N, state_type) -> None:
        self.N = N
        self.state_type = state_type

        # Initialise 2D array of state depending on user input
        if self.state_type == 0:
            self.state = np.random.choice(2, size=(self.N, self.N))
        elif self.state_type == 1:
            self.state = self.make_blinker_corners() + self.make_glider_centre()
        elif self.state_type == 2:
            self.state = self.make_glider_side()

    def make_glider_centre(self):
        state = np.zeros((self.N, self.N), int)
        centre = int(np.around(self.N/2))
        state[centre-1][centre] = 1
        state[centre][centre+1] = 1
        state[centre+1][centre+1] = 1
        state[centre+1][centre] = 1
        state[centre+1][centre-1] = 1
        return state

    def make_glider_side(self):
        state = np.zeros((self.N, self.N), int)
        centre = int(np.around(self.N/2))
        state[centre-21][centre] = 1
        state[centre-20][centre+1] = 1
        state[centre-19][centre+1] = 1
        state[centre-19][centre] = 1
        state[centre-19][centre-1] = 1
        return state

    def make_blinker_corners(self):
        state = np.zeros((self.N, self.N))
        quarter = int(np.around(self.N / 4))
        three_quarter = 3 * quarter
        state[quarter-1][three_quarter] = 1
        state[quarter][three_quarter] = 1
        state[quarter+1][three_quarter] = 1
        state[three_quarter-1][quarter] = 1
        state[three_quarter][quarter] = 1
        state[three_quarter+1][quarter] = 1
        return state
    
    def get_alive_nn(self):
        # Gives array that has number of alive nn at each position
        left = np.roll(self.state, 1, axis=1)
        right = np.roll(self.state, -1, axis=1)
        top = np.roll(self.state, 1, axis=0)
        bottom = np.roll(self.state, -1, axis=0)
        top_left = np.roll(self.state, (1,1), axis=(1,0))
        top_right = np.roll(self.state, (-1,1), axis=(1,0))
        bottom_left = np.roll(self.state, (1,-1), axis=(1,0))
        bottom_right = np.roll(self.state, (-1,-1), axis=(1,0))
        alive_nn = left + right + top + bottom + top_left + top_right + bottom_left + bottom_right
        return alive_nn

    def update_state(self):
        alive_nn = self.get_alive_nn()
        mask_still_alive = np.logical_or(alive_nn == 2, alive_nn == 3) # Gives true for all spots that have 2 or 3 nn, regardless of whether dead or alive
        become_alive = np.logical_and(alive_nn == 3, self.state == 0) # Gives true if live_nn is 3 and was previously dead
        self.state = self.state * mask_still_alive + become_alive # Mask needs to be multiplied elementwise to only give 1s where there was a 1 before
        alive_total = np.count_nonzero(self.state == 1)
        return alive_total

    def run(self, n_sweeps):
        # Initialise figure, uncomment to plot
        fig = plt.figure()
        im = plt.imshow(self.state, animated=True, vmin=0, vmax=1)

        alive_total = []
        counter = 0
        for i in range(n_sweeps):
            alive = self.update_state()
            alive_total.append(alive)
            
            print(f"Step {i:d}")
            plt.cla()
            im = plt.imshow(self.state, animated=True, vmin=0, vmax=1)
            plt.draw()
            plt.pause(1e-10)

            if alive == alive_total[i-1]:
                counter += 1
        return alive_total

    def sweep(self):
        for _ in range(1000):
            self.run(1000)

    def measure_alive(self, n_sweeps):
        alive_total = []
        counter = 0
        for i in range(n_sweeps):
            alive = self.update_state()
            alive_total.append(alive)

            if alive == alive_total[i-1]:
                counter += 1

            if counter == 10:
                i = i
                break
        return i

    def measure(self, n_sweeps):
        equilibrium = []
        for _ in range(500):
            self.state = np.random.choice(2, size=(self.N, self.N))
            i = self.measure_alive(n_sweeps)
            equilibrium.append(i)
        return equilibrium

    def calc_velocity(self, n_sweeps):
        #self.state = self.make_glider_side()
        com_xs = []
        com_ys = []
        for i in range(n_sweeps):
            _ = self.update_state()
            if i % 10 == 0:
                ys, xs = np.where(self.state == 1)
                com_y = np.sum(ys) / len(ys)
                com_ys.append(com_y)
                if (abs(xs[-1] - xs[1]) > (self.N - 3)): # check that difference between x and y values is smaller than approx. size of 2d array
                    continue
                else: # if not, calculate com and append
                    com_x = np.sum(xs) / len(xs)
                    com_xs.append(com_x)
        vel_x = (com_xs[9] - com_xs[0]) / 90
        vel_y = (com_ys[9] - com_ys[0]) / 90
        v = np.sqrt(vel_x **2 + vel_y ** 2)
        return com_xs, com_ys, vel_x, vel_y, v

# Main entry point of the program
if __name__ == "__main__":
    
    # Read input arguments
    args = sys.argv
    if (len(args) != 3):
        print("Usage gameoflife.py N state_type")
        sys.exit(1)
    N = int(args[1])
    state_type = int(args[2])

    # Set up and run the visualisation
    model = GameOfLife(N, state_type)
    # alive_total = model.run(1000)

    # Number of alive cells plot
    x = np.arange(1000)
    plt.scatter(x, alive_total, color="darkorchid")
    plt.gca().invert_yaxis()
    plt.ylabel("Alive Cells")
    plt.xlabel("Update")
    #plt.legend(loc='best')
    plt.show()

    # Histogram of frequency of runs of certain length until equilibrium
    eq = model.measure(1000)
    fig = plt.hist(eq, bins=30, color='darkorchid')
    plt.show()

    # COM plot, select glider with state=2 when prompted
    com_x, com_y, vel_x, vel_y, v = model.calc_velocity(1000)
    t = np.arange(len(com_x))
    fig_2 = plt.scatter(t, com_x, marker='x', color="darkorchid")
    plt.title("COM x")
    plt.show()

    t = np.arange(len(com_y))
    fig_3 = plt.scatter(t, com_y, marker='x', color="darkorchid")
    plt.title("COM y")
    plt.show()

    print(vel_x)
    print(vel_y)
    print(v)
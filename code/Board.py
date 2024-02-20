import plotly.graph_objects as go
from IPython import display

class Board:
    def __init__(self,
                board,
                board_size,
                current_player,
                last_move,
                display_mode_view = '3d',
                ):
                self.board = board
                self.current_player = current_player
                self.last_move = last_move
                self.board_size = board_size
                self.display_mode_view = display_mode_view

    def display_board(self, last_move, current_player):
        if self.display_mode_view == '2d':
            self.plot_go_board()

        if self.display_mode_view == '3d':
            self.plot_go_board_3d(last_move= last_move, current_player=current_player)

        else:
            print("Invalid choice. View does not exist. Choose from 2D and 3D.")

    def plot_go_board(self, last_move="", current_player=None):
        last_move_text = "" if last_move == "" else f"Last move: {last_move} by {current_player}"

        for z in range(self.board_size):
            print(f"\nLayer {z+1}:\n")

            # Print X-axis labels (A, B, C, ...)
            x_axis_labels = '   ' + ' '.join([chr(65 + x) for x in range(self.board_size)])
            print(x_axis_labels)

            for y in range(self.board_size):
                row = f"{y + 1:2d} "  # Y-axis labels (1, 2, 3, ...)
                for x in range(self.board_size):
                    if self.board[x, y, z] == 0:
                        row += '. '
                    elif self.board[x, y, z] == 1:
                        row += 'B '
                    elif self.board[x, y, z] == 2:
                        row += 'W '
                print(row)

    def plot_go_board_3d(self, last_move="", current_player=None):
        # Clear the previous figure
        display.clear_output(wait=True)

        last_move_text = "" if last_move == "" else f"Last move: {last_move} by {current_player}"

        traces = []

        # Iterate through each node to draw lines, text, and stones with outlines
        for x in range(self.board_size):
            for y in range(self.board_size):
                for z in range(self.board_size):
                    node_name = f"{chr(65 + x)}{y + 1}-{z + 1}"

                    # Draw stones with black outlines
                    if self.board[x, y, z] != 0:
                        color = 'black' if self.board[x, y, z] == 1 else 'white'
                        traces.append(go.Scatter3d(x=[x], y=[y], z=[z], mode='markers',
                                                   marker=dict(size=10, color=color, opacity=1.0,
                                                               line=dict(width=2, color='black')),
                                                   showlegend=False))
                    else:
                        traces.append(go.Scatter3d(x=[x], y=[y], z=[z], mode='text', text=[node_name],
                                                   textfont=dict(color='black', size=10),
                                                   showlegend=False))

                    # Draw lines to adjacent nodes
                    if x < self.board_size - 1:
                        traces.append(go.Scatter3d(x=[x, x + 1], y=[y, y], z=[z, z],
                                                   mode='lines', line=dict(color='black', width=1),
                                                   showlegend=False))
                    if y < self.board_size - 1:
                        traces.append(go.Scatter3d(x=[x, x], y=[y, y + 1], z=[z, z],
                                                   mode='lines', line=dict(color='black', width=1),
                                                   showlegend=False))
                    if z < self.board_size - 1:
                        traces.append(go.Scatter3d(x=[x, x], y=[y, y], z=[z, z + 1],
                                                   mode='lines', line=dict(color='black', width=1),
                                                   showlegend=False))

        # Adjust the layout to make the figure vertically larger
        layout = go.Layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False),
                                      aspectmode='cube', camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))),
                           margin=dict(l=0, r=0, b=0, t=0), showlegend=False)

        fig = go.Figure(data=traces, layout=layout)

        # Isometric view settings
        camera = dict(
            eye=dict(x=1.55, y=1.25, z=1.25),  # A rough approximation for isometric view
            up=dict(x=0, y=0, z=1),  # Ensures that Z axis is up
        )

        fig.update_layout(
            height = 600,
            scene_camera=camera,
            scene=dict(
                xaxis_title='X',
                yaxis_title='Y',
                zaxis_title='Layer',
                aspectmode='cube'
            ),
            annotations=[
                dict(
                    text=last_move_text,
                    showarrow=False,
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=-0.1,
                    xanchor="center",
                    yanchor="top",
                    font=dict(size=14, color='black')
                )
            ],
            margin=dict(b=100)
        )

        fig.show()

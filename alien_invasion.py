import sys
import pygame
from time import sleep
from game_stats import GameStats
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from button import Button
from scoreboard import Scoreboard

class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        
        self.settings = Settings()
        self.screen = self.settings.screen
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasioin")
        
        # Create an instance to store game statistics, 
        # and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
    
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        
        self._create_fleet()
    
        #make the Play button.
        self.play_button = Button(self, "Play")
        
    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            
            self._update_screen()
            
            
    def _check_events(self):
        """Responds to keypresses and mouse events."""
        # Watch for keyboard and mouse events.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._set_high_score(self.stats.high_score)
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
                
    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_setting()
            # Reset the game stats.
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_images()
            
            #Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()
            
            #Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            #Hide the mouse cursor.
            pygame.mouse.set_visible(False)
            
    def _check_keydown_events(self, event):
        """"Respond to keypresses."""                
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self._set_high_score(self.stats.high_score)
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self,event):
        """"Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
    
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:        
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
            # Update bullet positions.
        self.bullets.update()
            
            # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        
        self._check_bullet_alien_collisions()
        
    def _check_bullet_alien_collisions(self):
        
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.aliens, True, True)
        
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        
        if not self.aliens:
            self.start_new_level()
            
    def start_new_level(self):
        """Gather all the ingredients for a new level."""
        self.bullets.empty()
        self._create_fleet()
        self.settings.increase_speed()
        # Increase level
        self.stats.level += 1
        self.sb.prep_level()
                                
    def _update_aliens(self):
        """
        Check if the fleet in at an edge, 
        then update the positions of all aliens in the fleet.
        """
        self._check_fleet_edges()
        self.aliens.update()
        
        # look for alien-ship collisions
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
            
        # Look for aliens hitting the bottom.
        self._check_aliens_bottom()
            
    def _ship_hit(self):
        """Response to ship being hit by aliens."""
        if self.stats.ships_left > 0:
            # Decrement ships left.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            
            # Get rid of remaining stuff.
            self.aliens.empty()
            self.bullets.empty()
            
            # Create new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            
            # pause
            sleep(0.5)
        
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)
    
    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat it as if ship hit.
                self._ship_hit()
                break
            
    def _create_fleet(self):
        """Create the fleet of aliens."""
        # create an alien and find the number of aliens in a row.
        # Spacing between each alien is equal to one alien width.
        
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)
        
        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - 
                                (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        
        # create fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)
    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
            
    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1
                    
    def _create_alien(self, alien_number, row_number): 
        """"Create an alien and place it in the row."""   
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)
    
    def _set_high_score(self, high_score):
        high_score = self.stats.high_score
        filename = "HS.txt"
        with open(filename, "w") as file_object:
            file_object.write(str(high_score))    
                    
    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        self.ship.update()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)
        self.sb.show_score()
        
        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()
        
        pygame.display.flip()
    
if __name__=="__main__":
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
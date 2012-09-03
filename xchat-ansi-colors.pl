use 5.010;
use strict;
use warnings;
use Xchat qw(:all);

register(
	"ANSI Color Converter",
	"0.000001",
	"Attempt to convert ANSI color codes",
);

#qw(black red green yelllow blue magenta cyan white);
my @colors = (qw(01 05 09 08 02 13 11), '');

hook_print( "Channel Message", \&convert_ansi, { data => "Channel Message" } );
hook_print( "Channel Action", \&convert_ansi, { data => "Channel Action" } );

sub convert_ansi {
	my ($nick, $text, $mode, $id_text) = @{$_[0]};
	my $event = $_[1];

	my @parts = split /(\e\[ \d{1,2} (?: ; \d{1,2})*  m)/x, $text;
	my $converted_text = ansi2irc( @parts );

	if( $converted_text ne $text ) {
		emit_print( $event, $nick, $converted_text, $mode, $id_text );
		return EAT_ALL;
	} else {
		return EAT_NONE;
	}
}

sub ansi2irc {
	my @parts = @_;

	my @irc_text;
	my ($underline, $bold, $reverse) = (0, 0, 0);

	for my $part ( @parts ) {
		if( $part =~ /\e\[ (\d{1,2} (?: ; \d{1,2})* ) m/x ) {
			given( $1 ) {
				when( [ 0 ] ) { # all attributes off
					push @irc_text, "\cO";
				}

				when( 1 ) { # bright/bold
					push @irc_text, "\cB";
				}

				when( 4 ) { # underline
					push @irc_text, "\c_";
					$underline = 1;
				}

				when( 7 ) { # reverse/inverse
					push @irc_text, "\cV";
					$reverse = 1;
				}

				when( 22 ) { # normal color
					push @irc_text, "\cC";

				}

				when( 24 && $underline ) { # remove underline
					push @irc_text, "\c_";
					$underline = 0;
				}

				when( 27 && $reverse ) {	# positive / undo inverse
					push @irc_text, "\cV";
					$reverse = 0;
				}

				when( [ 30 .. 37 ] ) { # set color
					my $color = $colors[ $_ - 30 ];
					push @irc_text, "\cC".$color;
				}

				when( [ 40 .. 47 ] ) { # set background color
					my $color = $colors[ $_ - 40 ];
					push @irc_text, "\cC,".$color;
				}

				default {
					push @irc_text, "unrecognized code '$_'";
				}
			}
		} else {
			push @irc_text, $part;
		}
	}

	return join "", @irc_text;
}

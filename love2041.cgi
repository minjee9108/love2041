#!/usr/bin/perl -w

# Assignment2
# Min Jee Son z3330687

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;
use File::Copy qw/move/;
use List::Util qw/min max/;
use IO::Handle;


warningsToBrowser(1);

# print start of HTML ASAP to assist debugging if there is an error in the script
print page_header();

# some globals used through the script
our $debug = 1;
our $students_dir = "./students";
our @students = glob("$students_dir/*");
our %data;
our $safe_chars = "a-zA-Z0-9_.-";

if(defined(param('page')) and defined(param('user'))){
  print menu(), p;
  if (param('page') eq "browse_ten"){
    print browse_ten();
  }elsif(param('page') eq "match"){
    print match();
  }elsif(param('page') eq "browse_screen"){
    print browse_screen();
  }elsif(param('page') eq "check_preferences"){
    print check_preferences();
  }elsif(param('page') eq "change_password1"){
    print change_password1();
  }elsif(param('page') eq "change_password2"){
    print change_password2();
  }elsif(param('page') eq "change_password3"){
    print change_password3();
  }elsif(param('page') eq "photo_check"){
    print photo_check();
  }elsif(param('page') eq "delete_photos"){
    print delete_photos();
  }elsif(param('page') eq "view_photo"){
    print view_photo();
  }elsif(param('page') eq "view_photo_check"){
    print view_photo_check();
  }elsif(param('page') eq "view_student"){
    print view_student();
  }elsif(param('page') eq "message_write"){
    print message_write();
  }elsif(param('page') eq "message_send"){
    print message_send();
  }elsif(param('page') eq "view_student_photo"){
    print view_student_photo();
  }
}
elsif(defined(param('page'))){
  if(param('page') eq "register_check"){
    print h2("New account"), register_check();
  }elsif(param('page') eq "new_profile"){
    print h2("New account"), new_profile();
  }elsif(param('page') eq "check_profile"){
    print h2("New account"), check_profile();
  }elsif(param('page') eq "retrieve_password2"){
    print retrieve_password2();
  }
}
elsif(defined(param('Skip this step'))){
  print menu();
}
elsif(defined(param('username')) and defined(param('password'))){
  print login_check();
}
elsif(defined(param('forgot your password?'))){
  print retrieve_password1();
}
elsif (defined(param('menu'))){
  if (param('menu') eq "logout"){
    print login();
  }else{
    print menu(), p;
    if(param('menu') eq "manage account"){
      print manage_account();
    }elsif(param('menu') eq "upload photos"){
      print upload_photos();
    }elsif(param('menu') eq "view photos"){
      print view_photos();
    }
    #print "</table>";
  }
}
elsif(defined(param('search'))){
  print menu(),p,search();
}
elsif(defined(param('register'))){
  print h2("New account"),
  register("",""); #username, email address
}
elsif(!defined(param('user'))){
  print login();
}

print page_trailer();
exit 0;

sub login {
  return start_form,
  center(
  p,
  'Username: ', textfield('username'),p,
  'Password: ', password_field('password'), "\n",
  "<table><tr><td>",submit('login')),
  end_form,"<td>",
  start_form,
  submit('register'),"<td>",
  submit('forgot your password?'),
  end_form,
  "</table>";
}

sub login_check {
  my $username = param('username');
  my $password = param('password');
  unless (-d "$students_dir/$username"){
    return "Unknown user. Try again",
    p,
    login();
  }
  open my $account, "$students_dir/$username/profile.txt";
  while (my $line = <$account>){
    if ($line =~ /^password:\s*$/){
      $line = <$account>;
      $line =~ s/^\s*|\s*$//g;
      if ($line ne $password){
        return "Incorrect password. Try again",
        login();
      }
      else{
        param('user', $username);
        return "Hello $username!",
        menu(),p ,match();
      }
    }
  }
}

sub menu{
  my $username = param('user');
  my $url = self_url;
  $url=~s/\/love2041\.cgi.*$//;
  $url.="/love2041.cgi?user=$username";
  return "<table><tr><td>",
  "<ul id=\"menu\"><li><a href=\"$url"."&page=browse_screen&user_search=$username\">your profile</a><ul>",
    "<li><a href=\"$url"."&page=browse_screen&user_search=$username\">view profile</a></li>",
    "<li><a href=\"$url"."&menu=view+photos\">view photos</a></li>",
    "<li><a href=\"$url"."&menu=upload+photos\">upload photos</a></li>",
    "</ul></li>",
  "<li><a href=\"$url"."&page=match\">view your matches</a></li>",
  "<li><a href=\"$url"."&menu=manage+account&user_search=$username\">manage account</a><ul>",
    "<li><a href=\"$url"."&page=change_password1\">change password</a></li>",
    "</ul></li>",
  "<li><a href = \"$url"."&menu=logout\">logout</a></li>",
  "</ul>",
  "<Td>",
  start_form('GET'),
  hidden('user'),
  'Search for: ', textfield('search'),"\n",
  submit,
  "</table>",
  p,
  end_form;

  
  return p,
  start_form('GET'),
  hidden('user'),
  popup_menu('menu', ["$username", "manage account", "upload photos", "view photos","logout"], "$username"),
  submit,
  end_form,
  start_form('GET'),
  hidden('user'),
  'Search for: ', textfield('search'),"\n",
  submit,
  p,
  end_form;

}

sub search{
  my $user_search = param('search');
  my $user = param('user');
  my %search; my $image; my $profile_image;
  my $output = "<table>";
  foreach my $student (@students){
    if ($student =~ /$students_dir\/.*$user_search/i){
      $search{$student}=length($user_search)/length($student);
    }
  }
  foreach my $student_to_show (reverse sort {$search{$a} <=> $search{$b}} keys %search){
    my $current_student = $student_to_show;
    $current_student=~ s/^$students_dir\///;
    if(-e "$student_to_show/profile.jpg"){
      $profile_image = "$student_to_show/profile.jpg";
    }else{
      $profile_image = "./no_image.jpg";
    }
    $data{$student_to_show}{"image"}="<html><img style = \"width:250px;\" src=\"$profile_image\"></html>";
    open my $p, "$student_to_show/profile.txt" or die "can not open $student_to_show/profile.txt: $!";
    while(my $line = <$p>){
      my @lines;
      while ($line =~ /^([^\s]+):\s*$/){
        my $info = $1;
        $line = <$p>;
      INNER:
        while ($line =~ /^\s+/){
          push @lines, $line;
          last INNER if eof();
          $line = <$p>;#
        }
        $data{$student_to_show}{$info}= join '', @lines;
        @lines = ();
      }
    }
    close $p;
    my @list = ('username', "gender", "hair_colour", "birthdate");
    my @profile;
    foreach my $heading (@list){
      if (defined($data{$student_to_show}{$heading})){
        push @profile, "$heading:\n$data{$student_to_show}{$heading}";
      }
    }
    my $profile = join '', (@profile);
    @profile = ();
    $output.="<tr><td><form action=\"love2041.cgi\" method=\"GET\"><a href=\"javascript:;\" onclick=\"parentNode.submit();\">$data{$student_to_show}{\"image\"}</a><input type=\"hidden\" name=\"user\" value=\"$user\"><input type=\"hidden\" name=\"page\" value=\"browse_screen\"><input type=\"hidden\" name=\"user_search\" value=\"$current_student\"><td></form>".pre($profile)."\n";
  }
  $output.="</table>";
  return p,
  $output,"\n",
  p, "\n";
}

sub match{
  my $user = param('user');
  my $user_pref_file = "$students_dir/$user/preferences.txt";
  my $user_prof_file = "$students_dir/$user/profile.txt";
  my @list; my %user_pref; my %user_profile; my %student_profile; my %score; my $line; my $profile_image;
  my $year = localtime();
  my $info;
  $year =~ /([0-9]{4})$/;
  $year=$1;
  if (-e $user_pref_file){
    open my $pref, "$user_pref_file" or die "can not open $user_pref_file :$!"; ## fix for when no preference.txt
    while($line = <$pref>){
      chomp $line;
      if ($line =~ /^([^\s]+):\s*$/){
        $user_pref{$info}= join ';', @list if defined($info);
        $info = $1;
        @list = ();
      }
      elsif($line =~ /^\s+min/){
        $line = <$pref>;
        my $min = $line;
        $min =~ s/[^0-9\.]//g;
        $line = <$pref>;
        $line = <$pref>;
        my $max = $line;
        $max =~ s/[^0-9\.]//g;
        $user_pref{$info} = "$min;$max" if eof();
        @list = ($min, $max);
      }
      else{
        $line =~ /^\s+(.+)\s*/;
        push @list, $1;
        $user_pref{$info}= join ';', @list if eof();
      }
    }
    close $pref;
  }
  return "Create your profile to find a match" if !(-e $user_prof_file);
  open my $prof, "$user_prof_file" or die "cannot open $user_prof_file :$!";
  my $info;
  while(my $line = <$prof>){
    chomp $line;
    if($line =~ /^([^\s]+):\s*$/){
      $user_profile{$info} = join ';', @list if defined($info);
      $info = $1;
      @list=();
    }else{
      $line =~ /^\s+(.+)\s*/;
      push @list, $1;
      $user_profile{$info} = join ';', @list if eof();
    }
  }
  close $prof;
  foreach my $student (@students){
    next if $student eq "$students_dir/$user";
    my $student_pref_file ="$student/preferences.txt";
    my $student_prof_file = "$student/profile.txt";
    my %student_pref;
    my $info;
    if (-e $student_pref_file){
      open my $pref, "$student_pref_file" or die "can not open $student_pref_file: $!";
      while($line = <$pref>){
        chomp $line;
        if ($line =~ /^([^\s]+):\s*$/){
          $student_pref{$info}= join ';', @list if defined($info);
          $info = $1;
          @list = ();
        }
        elsif($line =~ /^\s+min/){
          $line = <$pref>;
          my $min = $line;
          $min =~ s/[^0-9\.]//g;
          $line = <$pref>;
          $line = <$pref>;
          my $max = $line;
          $max =~ s/[^0-9\.]//g;
          $student_pref{$info} = "$min;$max" if eof();
          @list = ($min, $max);
        }
        else{
          $line =~ /^\s+(.+)\s*/;
          push @list, $1;
          $student_pref{$info}= join ';', @list if eof();
        }
      }
      close $pref;
    }
    next if !(-e $student_prof_file);
    my $info;
    open my $prof, "$student_prof_file" or die "can not open $student_prof_file: $!";
    while(my $line = <$prof>){
      chomp $line;
      if($line =~ /^([^\s]+):\s*$/){
        $student_profile{$student}{$info} = join ';', @list if defined($info);
        $info = $1;
        @list=();
      }else{
        $line =~ /^\s+(.+)\s*/;
        push @list, $1;
        $student_profile{$student}{$info} = join ';', @list if eof();
      }
    }
    close $prof;
    if((defined($user_pref{"gender"}) and defined($student_profile{$student}{"gender"}) and $user_pref{"gender"} ne $student_profile{$student}{"gender"}) or (defined($student_pref{"gender"}) and defined($user_profile{"gender"}) and $student_pref{"gender"} ne $user_profile{"gender"})){
      next;
    }
    my $user_pref_match =0; #worth 0.4
    my $student_pref_match=0; #worth 0.4
    my $user_prof_match=0; #worth 0.2
    ## MATCH BASED ON USER'S PREFERENCE ##
    # age worth 0.4 of match based on user's preference

    if (!defined($user_pref{"age"})){
      $user_pref_match=0.4;
    }else{
      $student_profile{$student}{"birthdate"} =~ /([0-9]{4})/;
      my $student_age = $year - $1;
      my @age = split(/;/, $user_pref{"age"});
      if($age[0] <= $student_age and $age[1] >= $student_age){
        $user_pref_match=0.4;
      }elsif($age[1]+5 >= $student_age and $age[1] < $student_age){
        $user_pref_match = (1-($student_age-$age[1])/5)*0.4;
      }
    }
    # weight, height, hair colour each worth 0.2 of match based on user's preference
    my @list = ("weight", "height");
    foreach my $preference (@list){
      if (!defined($user_pref{$preference})){
        $user_pref_match+=0.2;
      }elsif(defined($student_profile{$student}{$preference})){
        my $body_type = $student_profile{$student}{$preference};
        $body_type =~ s/[^0-9\.]//g;
        my @pref_body_type = split(/;/,$user_pref{$preference});
        if($pref_body_type[0] <= $body_type and $pref_body_type[1] >= $body_type){
          $user_pref_match+=0.2;
        }
      }
    }
    if(!defined($user_pref{"hair_colours"})){
      $user_pref_match+=0.2;
    }elsif(defined($student_profile{$student}{"hair_colour"})){
      my @hair_colours = split(/;/,$user_pref{"hair_colours"});
      if(grep(/$student_profile{$student}{"hair_colour"}/i, @hair_colours)){
        $user_pref_match+=0.2;
      }
      
    }
    ## MATCH BASED ON STUDENT'S PREFERENCE ##
    if (!defined($student_pref{"age"})){
      $student_pref_match=0.4;
    }elsif(defined($user_profile{"birthdate"})){
      $user_profile{"birthdate"} =~ /([0-9]{4})/;
      my $user_age = $year - $1;
      my @age = split(/;/, $student_pref{"age"});
      if($age[0] <= $user_age and $age[1] >= $user_age){
        $student_pref_match=0.4;
      }elsif($age[1]+5 >= $user_age){
        $student_pref_match = (1-($user_age-$age[1])/5)*0.4;
      }else{
        $student_pref_match=0;
      }
    }
    # weight, height, hair colour each worth 0.2 of match based on user's preference
    my @list = ("weight", "height");
    foreach my $preference (@list){
      if (!defined($student_pref{$preference})){
        $student_pref_match+=0.2;
      }elsif(defined($user_profile{$preference})){
        my $body_type = $user_profile{$preference};
        $body_type =~ s/[^0-9\.]//g;
        my @pref_body_type = split(/;/,$student_pref{$preference});
        if($pref_body_type[0] <= $body_type and $pref_body_type[1] >= $body_type){
          $student_pref_match+=0.2;
        }
      }
    }
    if(!defined($student_pref{"hair_colours"})){
      $student_pref_match+=0.2;
    }elsif(defined($user_profile{"hair_colour"})){
      my @hair_colours = split(/;/,$student_pref{"hair_colours"});
      if(grep(/$user_profile{"hair_colour"}/i, @hair_colours)){
        $student_pref_match+=0.2;
      }
    }
    ## MATCH BASED ON THE PROFILES OF BOTH USER AND STUDENT
    # If age preference wasn't specified, age worth 0.4, hobbies 0.2, courses 0.1 and movies, books, tv shows and bands each worth 0.075 of match scored based on profiles
    if(!defined($user_pref{"age"})){
      #If user's birthdate is not specified, all students get full 0.4 for age
      if(!defined($user_profile{"birthdate"})){
        $user_prof_match+=0.4;
      }else{
        #No age match score given to student without a specified birthdate
        if(defined($student_profile{$student}{"birthdate"})){
          #Only consider marks when the age difference is less than 10 years
          $student_profile{$student}{"birthdate"} =~ /([0-9]{4})/;
          my $student_age = $year - $1;
          $user_profile{"birthdate"} =~ /([0-9]{4})/;
          my $user_age = $year - $1;
          if (max(18, $user_age-10) <= $student_age and $user_age+10 >= $student_age){ #NO UNDERAGE
            $user_prof_match += (1-abs($user_age-$student_age)/10)*0.4;
          }
        }
      }
      #hobbies
      if(defined($user_profile{"favourite_hobbies"}) and defined($student_profile{$student}{"favourite_hobbies"})){
        my @user_hobbies = split(/;/, $user_profile{"favourite_hobbies"});
        my @student_hobbies = split(/;/, $student_profile{$student}{"favourite_hobbies"});
        my @common_hobbies;
        foreach my $h (@user_hobbies){
          push @common_hobbies, grep(/$h/i, @student_hobbies);
        }
        $user_prof_match += ($#common_hobbies+1)/($#user_hobbies+1)*0.2;
      }
      #courses
      if(defined($user_profile{"courses"}) and defined($student_profile{$student}{"courses"})){
        my @user_courses = split(/;/, $user_profile{"courses"});
        @user_courses = map{$_ =~ /([A-Z]{4}[0-9]{4})/;$1}@user_courses;
        my @student_courses = split(/;/, $student_profile{$student}{"courses"});
        @student_courses = map{$_ =~ /([A-Z]{4}[0-9]{4})/;$1}@student_courses;
        my @common_courses;
        foreach my $h (@user_courses){
          push @common_courses, grep(/$h/i, @student_courses);
        }
        $user_prof_match += ($#common_courses+1)/($#user_courses+1)*0.1;
      }
      #favourite tv shows, movies, bands and books
      my @list = ("favourite_TV_shows", "favourite_bands", "favourite_movies", "favourite_books");
      foreach my $heading (@list){
        if(defined($user_profile{$heading}) and defined($student_profile{$student}{$heading})){
          my @user_heading = split(/;/, $user_profile{$heading});
          my @student_heading = split(/;/, $student_profile{$student}{$heading});
          my @common_heading;
          foreach my $h (@user_heading){
            push @common_heading, grep(/$h/i, @student_heading);
          }
          $user_prof_match += ($#common_heading+1)/($#user_heading+1)*0.075;
        }
      }
    }else{ #user pref for age was defined - 1/3 for hobbies, 1/6 for courses and 0.125 for tv shows, bands, books and movies
      if(defined($user_profile{"favourite_hobbies"}) and defined($student_profile{$student}{"favourite_hobbies"})){
        my @user_hobbies = split(/;/, $user_profile{"favourite_hobbies"});
        my @student_hobbies = split(/;/, $student_profile{$student}{"favourite_hobbies"});
        my @common_hobbies;
        foreach my $h (@user_hobbies){
          push @common_hobbies, grep(/$h/i, @student_hobbies);
        }
        $user_prof_match += ($#common_hobbies+1)/($#user_hobbies+1)*(1.0/3);
      }
      #courses
      if(defined($user_profile{"courses"}) and defined($student_profile{$student}{"courses"})){
        my @user_courses = split(/;/, $user_profile{"courses"});
        @user_courses = map{$_ =~ /([A-Za-z]{4}[0-9]{4})/;$1}@user_courses;
        my @student_courses = split(/;/, $student_profile{$student}{"courses"});
        @student_courses = map{$_ =~ /([A-Za-z]{4}[0-9]{4})/;$1}@student_courses;
        my @common_courses;
        foreach my $h (@user_courses){
          push @common_courses, grep(/$h/i, @student_courses);
        }
        $user_prof_match += ($#common_courses+1)/($#user_courses+1)*(1.0/6);
      }
      #favourite tv shows, movies, bands and books
      my @list = ("favourite_TV_shows", "favourite_bands", "favourite_movies", "favourite_books");
      foreach my $heading (@list){
        if(defined($user_profile{$heading}) and defined($student_profile{$student}{$heading})){
          my @user_heading = split(/;/, $user_profile{$heading});
          my @student_heading = split(/;/, $student_profile{$student}{$heading});
          my @common_heading;
          foreach my $h (@user_heading){
            push @common_heading, grep(/$h/i, @student_heading);
          }
          $user_prof_match += ($#common_heading+1)/($#user_heading+1)*0.125;
        }
      }
    }
    
    $score{$student}=$user_pref_match*0.4 + $student_pref_match*0.4 + $user_prof_match*0.2;
  }
  my @student_match = reverse sort {$score{$a} <=> $score{$b}} keys %score;
  return "No matches found.",p if $#student_match == -1;
  my $i = param('n') || param('p') || 0;
  $i = min(max($i, 0), $#student_match);
  my $j = min($#student_match, $i+9);
  my $output = "<table>";
  foreach my $student_to_show (@student_match[$i..$j]){
    my $current_student = $student_to_show;
    $current_student =~ s/^$students_dir\///g;
    if(-e "$student_to_show/profile.jpg"){
      $profile_image = "$student_to_show/profile.jpg";
    }else{
      $profile_image = "./no_image.jpg";
    }
    $student_profile{$student_to_show}{"image"}="<img style = \"width:250px;\" src=\"$profile_image\">";
    my @list = ('username', "gender", "hair_colour", "birthdate");
    my @profile;
    foreach my $heading (@list){
      if (defined($student_profile{$student_to_show}{$heading})){
        push @profile, "$heading:\n\t$student_profile{$student_to_show}{$heading}\n";
      }
    }
    push @profile, "match: $score{$student_to_show}"; # DELETE LATER!!
    my $profile = join '', (@profile);
    @profile = ();
    $output.="<tr><td><form action=\"love2041.cgi\" method=\"GET\"><a href=\"javascript:;\" onclick=\"parentNode.submit();\">$student_profile{$student_to_show}{\"image\"}</a><input type=\"hidden\" name=\"user\" value=\"$user\"><input type=\"hidden\" name=\"page\" value=\"browse_screen\"><input type=\"hidden\" name=\"user_search\" value=\"$current_student\"><td></form>".pre($profile)."\n";
  }
  $output.="</table>";
  param('n', $i+10);
  param('p', $i-10);
  param('page', "match");
  return p,
  $output,"\n",
  start_form("GET"),
  hidden('n'), hidden('user'), hidden('page'), "\n",
  submit('Next students'),"\n",
  end_form, "\n",
  start_form("GET"),
  hidden('p'), hidden('user'), hidden('page'), "\n",
  submit('Previous students'),
  end_form,
  p, "\n";
}
  

sub browse_screen {
  my $student_to_show; my $n; my $profile_image;
  if (defined(param('user_search'))){
    $student_to_show=param('user_search');
    $student_to_show="$students_dir/$student_to_show";
    ($n) = grep{$students[$_] eq $student_to_show} 0..$#students;
    param('n', $n+1);
  }
  else{
	$n = param('n') || 0;
	$n = min(max($n, 0), $#students);
	param('n', $n + 1);
	$student_to_show  = $students[$n];
  }
  if(-e "$student_to_show/profile.jpg"){
    $profile_image = "$student_to_show/profile.jpg";
  }else{
    $profile_image = "./no_image.jpg";
  }
  my $profile_filename = "$student_to_show/profile.txt";
    $data{$student_to_show}{"image"}="<img style = \"width:250px;\" src=\"$student_to_show/profile.jpg\">";
	open my $p, "$student_to_show/profile.txt" or die "can not open $profile_filename: $!";
	while(my $line = <$p>){
      while ($line =~ /^([^\s]+):\s*$/){
        my @lines;
        my $info = $1;
        $line = <$p>;
      INNER:
        while ($line =~ /^\s+/){
          push @lines, $line;
          last INNER if eof();
          $line = <$p>;
        }
        $data{$student_to_show}{$info}= join '', @lines;
        @lines = ();
      }
	}
	close $p;
  
    my @list = ('username', "gender", "hair_colour", "birthdate", "height", "weight", "about", "favourite_bands", "favourite_movies", "favourite_TV_shows", "favourite_books", "favourite_hobbies");
    my @profile;
    foreach my $heading (@list){
      if (defined($data{$student_to_show}{$heading})){
        push @profile, "$heading:\n$data{$student_to_show}{$heading}";
      }
    }
    my $profile = join '', (@profile);
    param('page', "view_student");
    param('email', $data{$student_to_show}{'email'});
	return p,
        "<img style = \"width:250px;\" src=\"$profile_image\">",
        start_form(),
        hidden('page'), hidden('user'), hidden('user_search'), hidden('email'),
        submit('message'),
        submit('view photos'), p,
		pre($profile),"\n",
		p, "\n";

}

sub browse_ten{
  my $n = param('n') || 0;
  my $user = param('user');
  $n = min(max($n, 0), $#students);
  my $profile; my $profile_image;
  my $output = "<table>";
  my $student_to_show;
  for (my $i = $n; $i <= $n+9; $i++){
    $student_to_show = $students[$i];
    my @profile = ();
    my $profile_filename = "$student_to_show/profile.txt";
    if(-e "$student_to_show/profile.jpg"){
      $profile_image = "$student_to_show/profile.jpg";
    }else{
      $profile_image = "./no_image.jpg";
    }
    $data{$student_to_show}{"image"}="<html><img style = \"width:250px;\" src=\"$student_to_show/profile.jpg\"></html>";
    open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
    while(my $line = <$p>){
      while ($line =~ /^([^\s]+):\s*$/){
        my @lines;
        my $info = $1;
        $line = <$p>;
      INNER:
        while ($line =~ /^\s+/){
          push @lines, $line;
          last INNER if eof();
          $line = <$p>;
        }
        $data{$student_to_show}{$info}= join '', @lines;
        @lines = ();
      }
    }
    close $p;
    my @list = ('username', "gender", "hair_colour", "birthdate");
    foreach my $heading (@list){
      if (defined($data{$student_to_show}{$heading})){
        push @profile, "$heading:\n$data{$student_to_show}{$heading}";
      }
    }
    $profile = join '', (@profile);
    param('page', "browse_screen");
    param('n', $i);
    $output.="<tr><td><form action=\"love2041.cgi\" method=\"GET\"><a href=\"javascript:;\" onclick=\"parentNode.submit();\">$data{$student_to_show}{\"image\"}</a><input type=\"hidden\" name=\"user\" value=\"$user\"><input type=\"hidden\" name=\"page\" value=\"browse_screen\"><input type=\"hidden\" name=\"n\" value=\"$i\"><td></form>".pre($profile)."\n";
  }
  $output.="</table>";
  param('n', $n+10);
  param('page', "browse_ten");
  return p,
        $output,"\n",
        start_form("GET"),
        hidden('n'), hidden('user'), hidden('page'), "\n",
        submit('Next students'),"\n",
        end_form, "\n",
        p, "\n";

}

sub register($$){
  my $username = @_[0];
  my $email = @_[1];
  param('page', "register_check");
  return p,
  center(
  start_form("GET"),
  hidden('page'),
  "Username: ", textfield(-name=>'newuser', -value=>"$username"),p,
  "Password: ", password_field('password1'), p,
  "Confirm your password: ", password_field('password2'), p,
  "E-mail: ", textfield(-name=>'email', -value=>"$email"), p,
  submit('submit'),
  end_form),
  p;
}
sub register_check(){
  my $username = param('newuser');
  my $email = param('email');
  my $password1 = param('password1');
  my $password2 = param('password2');
  if (param('newuser') eq "" or param('email') eq "" or param('password1') eq "" or param('password2') eq ""){
    return p,
    "<font color =\"red\">Please enter all details.</font>",
    register("","");
  }elsif(-d "$students_dir/$username"){
    return p,
    "<font color =\"red\">Username already exists.</font>",
    register("",$email);
  }elsif($password1 ne $password2){
    return p,
    "<font color =\"red\">Passwords don't match.</font>",
    register($username, $email);
  }elsif($username =~ /[^A-Za-z0-9_]/){
    return p,
    "<font color =\"red\">Username can't have any special characters.</font>",
    register("", $email)
  }elsif($email !~ /^[^\s]+\@[^\s]+$/){
    return p,
    "<font color =\"red\">Please provide a valid email address.</font>",
    register($username, "");
  }else{
    $email = substr($email, 0, 256);
    $email =~ s/[^\w\.\@\-\!\#\$\%\&\'\*\+\-\/\=\?\^_\`\{\|\}\~]//g;
    my $link = self_url;
    $link=~s/\/love2041\.cgi.*$//;
    $link .= "/love2041.cgi?page=new_profile&username=$username&password=$password1&email=$email";
    open MAIL, '|-','mail','-s','LOVE2041 Email Verification',$email or die "Can not run email";
    print MAIL "Click the link to complete your account verification.\n$link\n";
    return p,
    "An email has been sent to you. Follow the link to verify your email address",
    p;
  }  
}
sub new_profile(){
  param('page', "check_profile"),
  return p,
  "Enter your details to complete your profile.",
  start_multipart_form(),
  hidden('username'), hidden('password'), hidden('email'), hidden('page'),
  "name: ", textfield('name'),p,
  "gender: ", radio_group('gender', ['female', 'male', 'other']),p,
  "birthdate: ", textfield('birthdate'), "dd/mm/yyyy",p,
  "Upload your profile picture: ", filefield('profileimg'), p,
  "weight: ", textfield('weight'), "kg", p,
  "height: ", textfield('height'), "m", p,
  "hair colour: ", radio_group('hair_colour', ['black', 'brown', 'red', 'blonde']), " or other: ", textfield('hair_colour'),p,
  "degree: ", textfield('degree'), p,
  "about: ", p, textarea('about', '', 20, 30),p, #profile text
  "<B>For the following sections, enter each entry on a new line</b>", p,
  "<table><tr><td valign \"top\">courses:<br>(Format example: 2014 S1 COMP2041) <td>", p, textarea('courses', '', 20, 30), p,"</table>",p,
  "<table><tr><td>favourite books: ",p, textarea('favourite_books', '', 20, 30), p,
  "<td>favourite movies: ",p, textarea('favourite_movies', '', 20, 30),p,
  "<td>favourite TV shows: ",p, textarea('favourite_TV_shows', '', 20, 30), p,
  "<td>favourite hobbies: ",p, textarea('favourite_hobbies', '', 20, 30), p, "</table>",
  submit('submit'),p,
  end_multipart_form;
}
sub check_profile(){
  my $err_msg = "";
  if(defined param('birthdate') && param('birthdate') !~ /^[0-3][0-9]\/(0[1-9]|1[0-2])\/[0-9]{4}$/){
    $err_msg=p."<font color = \"red\">Enter in a valid birthdate in the form dd/mm/yyyy</font>";
  }
  if(param('weight') =~ /[^0-9\.]/){
    $err_msg.=p."<font color = \"red\">Enter in the weight in a numeric form</font>";
  }
  if(param('height') =~ /[^0-9\.]/){
    $err_msg .= p."<font color = \"red\">Enter in the height in a numeric form</font>";
  }
  if(defined param('profileimg') && param('profileimg') !~ /\.(jpg)$/){
    $err_msg .= p."<font color = \"red\">Profile image must be jpeg</font>";
  }
  return $err_msg, new_profile() if($err_msg ne "");
  my $username = param('username');
  my $student_folder = "$students_dir/$username";
  mkdir $student_folder or die "$student_folder could not be created: $!";
  my $profile = "$student_folder/profile.txt";
  my $profileimg = "$student_folder/profile.jpg";
  my $file = param('profileimg');
  my ($bytesread, $buffer);
  open(OUTFILE, ">", "$profileimg") or die "Couldn't open $profileimg for writing:$!";
  while($bytesread = read($file, $buffer, 1024)){
    print OUTFILE $buffer;
  }
  close OUTFILE;
  open F, '>', $profile or die "$profile could not be created: $!";
  my @params = param();
  foreach my $param_name (@params){
    next if $param_name eq 'submit' or $param_name eq 'page' or $param_name eq 'profileimg';
    if(param($param_name) ne ""){
      my $val = param($param_name);
      if ($param_name eq "weight"){
        $val.="kg";
      }elsif($param_name eq "height"){
        $val.="m";
      }elsif($param_name eq "courses" or $param_name eq "favourite_books" or $param_name eq "favourite_movies" or $param_name eq "favourite_TV_shows" or $param_name eq "favourite_hobbies"){
        $val =~ s/\s*\r\s*/\n\t/g;
      }elsif($param_name eq "about"){
        $val =~ s/\s*\r\s*/<br>\n\t/g;
        while ($val =~ /(<[^>]+>)/g){
          my $html = $1;
          next if $html =~ /<\/?font[^>]*>|<\/?b>|<\/?i>|<\/?u>|<\/?em>|<\/?strong>/i;
          $val =~ s/$html//g;
        }
      }
      print F "$param_name:\n\t".$val."\n" if param($param_name) ne "";
    }
  }
  return new_preferences();
}

sub new_preferences(){
  param('user', param('username'));
  param('page', "check_preferences");
  return p,
  "Tell us your preferences for a more accurate match.", p,
  start_form('GET'),
  hidden('user'), hidden('page'),
  "gender: ", checkbox_group('gender', ['female', 'male', 'other']),p,
  "age: min: ", textfield('age_min'), "max: ", textfield('age_max'),p,
  "height: min: ", textfield('height_min'), "m max: ", textfield('height_max'), "m",p,
  "weight: min: ", textfield('weight_min'), "kg max: ", textfield('weight_max'), "kg",p,
  "hair colours: ", checkbox_group('hair_colours', ['black', 'brown', 'red', 'blonde']), " or other: ", textfield('hair_colours_other'),p,
  submit('submit'),p,
  end_form,
  start_form('GET'),
  hidden('user'),
  submit('Skip this step'),p,
  end_form;
}

sub check_preferences(){
  my $err_msg = "";
  my $username = param('user');
  my $student_folder = "$students_dir/$username";
  my $preferences = "$student_folder/preferences.txt";
  if (!defined(param('Skip this step'))){
    if(param('age_min') =~ /[^0-9]/ or param('age_max') =~ /[^0-9]/){
      $err_msg=p."<font color = \"red\">Enter in the age in a numeric form</font>";
    }
    if(param('weight_min') =~ /[^0-9\.]/ or param('weight_max') =~ /[^0-9\.]/){
      $err_msg=p."<font color = \"red\">Enter in the weight in a numeric form</font>";
    }
    if(param('height_min') =~ /[^0-9\.]/ or param('height_max') =~ /[^0-9\.]/){
      $err_msg = p."<font color = \"red\">Enter in the height in a numeric form</font>";
    }
    return $err_msg, new_preferences() if($err_msg ne "");
    open F, '>', $preferences or die "$preferences could not be created: $!";
    my @params = param();
    foreach my $param_name (@params){
      next if $param_name eq 'submit' or $param_name eq 'page' or $param_name eq 'user';
      if(param($param_name) ne ""){
        my $val = param($param_name);
        $val =~ s/^\s*|\s*$//g;
        if ($param_name eq "weight_min"){
          $val.="kg";
          print F "weight:\n\tmin:\n\t\t$val\n";
        }elsif ($param_name eq "weight_max"){
          $val.="kg";
          print F "\tmax:\n\t\t$val\n";
        }elsif($param_name eq "height_min"){
          $val.="m";
          print F "height:\n\tmin:\n\t\t$val\n";
        }elsif($param_name eq "height_max"){
          $val.="m";
          print F "\tmax:\n\t\t$val\n";
        }elsif($param_name eq "age_min"){
          print F "age:\n\tmin:\n\t\t$val\n";
        }elsif($param_name eq "age_max"){
          print F "\tmax:\n\t\t$val\n";
        }elsif($param_name eq "hair_colours" or $param_name eq "gender"){
          $val = join("\n\t", param($param_name));
          print F "$param_name:\n\t".$val."\n";
        }elsif($param_name eq "hair_colours_other"){
          print F "\t$val\n";
        }
      }
    }
  }
  return p,
  "Complete!";
}

sub retrieve_password1(){
  param('page', "retrieve_password2");
  return p,
  start_form('GET'),
  hidden('page'),
  'Enter your username: ', textfield('username'),p,
  submit('submit'),
  end_form;
}
sub retrieve_password2(){
  my $username = param('username');
  my $student = "$students_dir/$username";
  my $email; my $password;
  if (!(-d "$student")){
    return p,
    "<font color = \"red\">Username does not exist.</font>",p,
    retrieve_password1();
  }else{
    open my $p, "$student/profile.txt" or die "Cannot open $student/profile: $!";
    while (my $line = <$p>){
      if ($line =~ /email:/){
        $line = <$p>;
        $line =~ /^\s+([^\s]+)\s*$/;
        $email = $1;
      }elsif($line =~ /password:/){
        $line = <$p>;
        $line =~ /^\s+([^\s]+)\s*$/;
        $password = $1;
      }
      if (defined($email) and defined($password)){
        last;
      }
    }
  }
  open MAIL, '|-','mail','-s','LOVE2041 Password Retrieval',$email or die "Can not run email";
  print MAIL "Your password is $password\n";
  return p,
  "Your password has been sent to your email.",
  p;
}
sub manage_account(){
  my $link = self_url;
  $link=~s/\/love2041\.cgi.*$//;
  my $username = param('user');
  $link .= "/love2041.cgi?page=change_password1&user=$username";
  return p,
  "<a href=\"$link\">Change Password</a>";
}
sub change_password1(){
  my $username = param('user');
  my $email;
  open my $p, "$students_dir/$username/profile.txt" or die "Cannot open $students_dir/$username/profile.txt: $!";
  while (my $line = <$p>){
    if($line =~ /email:/){
      $line = <$p>;
      $line =~ /^\s+([^\s]+)\s*$/;
      $email = $1;
      last;
    }
  }
  my $link = self_url;
  $link=~s/\/love2041\.cgi.*$//;
  $link .= "/love2041.cgi?page=change_password2&user=$username";
  open MAIL, '|-','mail','-s','LOVE2041 Password Retrieval',$email or die "Can not run email";
  print MAIL "Follow the link to change your password.\n$link\n";
  return p,
  "An email has been sent to you. Follow the link to change your password.",
  p;
}
sub change_password2(){
  param('page', "change_password3");
  return p,
  start_form('POST'),
  hidden('page'), hidden('user'),
  "Enter your new password: ", password_field('password1'), p,
  "Confirm your password: ", password_field('password2'), p,
  submit('submit'),
  end_form;
}
sub change_password3(){
  if (param('password1') ne param('password2')){
    return p,
    "<font color = \"red\">The passwords do not match each other.</font>",
    change_password2();
  }
  my $username = param('user');
  my $password = param('password1');
  open OLD, '<', "$students_dir/$username/profile.txt";
  open NEW, '>', "$students_dir/$username/profile.new.txt";
  while( <OLD> ){
    if ($_ =~ /^password:/){
      print NEW $_;
      print NEW "\t$password\n";
      <OLD>;
    }else{
      print NEW $_;
    }
  }
  close OLD;
  close NEW;
  unlink "$students_dir/$username/profile.txt";
  move "$students_dir/$username/profile.new.txt", "$students_dir/$username/profile.txt";
  return p,
  "Password has been changed.";
}
sub view_photos(){
  my $username = param('user');
  my @uploaded_photos = glob("$students_dir/$username/photo*.jpg");
  my $col = 0;
  my $profile_html='';
  my $photos_html ='';
  my $url = self_url;
  $url=~s/\/love2041\.cgi.*$//;
  $url.="/love2041.cgi?";
  if(-e "$students_dir/$username/profile.jpg"){
    $profile_html.="<img style = \"width:250px;\" src=\"$students_dir/$username/profile.jpg\">";
  }
  $profile_html .= submit('delete') if $profile_html ne "";
  $photos_html.="<table><tr>";
  foreach my $photo (@uploaded_photos){
    $photo =~ /$students_dir\/$username\/(.+)$/;
    my $photo_name = $1;
    my $photo_url = $url."page=view_photo&photo=$photo_name&user=$username";
    $photos_html .="<td><a href = \"$photo_url\"><img style = \"width: 250px;\" src = \"$photo\"></a><br>";
    $photos_html .= checkbox(-name=>"$photo_name", -checked=>0, -label=> '')."</td>";
    if ($col == 2){
      $col = 0;
      $photos_html.="</tr><tr>";
    }else{
      $col+=1;
    }
  }
  $photos_html.="</table>";
  $photos_html = "" if $photos_html eq "<table><tr></table>";
  $photos_html .= submit('delete selected photos') if $photos_html ne "";
  param('page', 'delete_photos');
  return p,
  start_form('GET'),
  hidden('page'), hidden('user'),
  h3("profile photo:"), "<br>",
  $profile_html,
  end_form,
  start_form('GET'),
  hidden('page'), hidden('user'),
  h3("photos:"),"<br>",
  $photos_html, "<br>",
  end_form;
}
sub view_photo(){
  my $username = param('user');
  my $photo_name = param('photo');
  param('page', 'view_photo_check');
  return p,
  start_form('GET'),
  hidden('page'), hidden('photo'), hidden('user'),
  submit('delete'), submit('make profile picture'),p,
  end_form,
  "<img src =\"$students_dir/$username/$photo_name\">";
}
sub view_photo_check(){
  my $username = param('user');
  my $photo_name = param('photo');
  my @photo_list = glob("$students_dir/$username/photo*.jpg");
  my $no_of_photos = $#photo_list;
  my $url = self_url;
  $url=~s/\/love2041\.cgi.*$//;
  $url.="/love2041.cgi?user=$username&menu=view+photos";
  $photo_name =~ /photo([0-9]{2})\.jpg/;
  my $photo_number = $1;
  $photo_number =~ s/^0//;
  if(defined param('delete')){
    unlink "$students_dir/$username/$photo_name";
  }elsif(defined param('make profile picture')){
    if(-e "$students_dir/$username/profile.jpg"){
      move "$students_dir/$username/profile.jpg", "$students_dir/$username/temp.jpg";
      move "$students_dir/$username/$photo_name", "$students_dir/$username/profile.jpg";
      move "$students_dir/$username/temp.jpg", "$students_dir/$username/$photo_name";
      return "<meta http-equiv=\"refresh\" content=\"0; url=$url\" />";
    }else{
       move "$students_dir/$username/$photo_name", "$students_dir/$username/profile.jpg";
    }
  }
  @photo_list = glob("$students_dir/$username/photo*.jpg");
  $no_of_photos = $#photo_list;
  for (my $i = $photo_number+1; $i<=$no_of_photos+1; $i++){
    my $new_photo_no = $i-1;
    my $move_photo = $photo_list[$i];
    $new_photo_no = "0".$new_photo_no if $new_photo_no =~ m/^[0-9]$/;
    move "$move_photo", "$students_dir/$username/photo$new_photo_no.jpg";
    $no_of_photos -= 1;
  }
  return "<meta http-equiv=\"refresh\" content=\"0; url=$url\" />";
}
sub upload_photos(){
  param('page', "photo_check");
  my $username = param('user');
  my $address = self_url;
  $address=~s/\/love2041\.cgi.*$//;
  $address .= "/love2041.cgi?menu=view+photos&user=$username";
  return p,
  "<a href = $address>View photos</a>", p,
  start_multipart_form,
  hidden('page'), hidden('user'),
  "Upload a new profile image:<br>",
  filefield('profileimg'),"<br><br>",
  "Upload photos:<br>", filefield('img1'), "<br>", filefield('img2'), "<br>", filefield('img3'), "<br>", filefield('img4'), "<br>", filefield('img5'),"<br><Br>",
  submit('upload'), p,
  end_multipart_form,p;
}
sub photo_check(){
  my $username = param('user');
  my $msg = "";
  my $file = param('profileimg');
  my $output_file = "$students_dir/$username/profile.jpg";
  if ($file ne ""){
    my ($bytesread, $buffer);
    my $username = param('user');
    #CHECK IF PROFILE IMG ALREADY EXISTS
    if(-e $output_file){
      my($photo_number, $photo_name);
      my @uploaded_photos=glob("$students_dir/$username/photo*.jpg");
      $photo_number = $#uploaded_photos+1;
      if ($photo_number>=100){
        $msg.="<font color =\"red\">Maximum number of photos exceeded. $file couldn't be uploaded.</font><br>";
      }else{
        if($photo_number<10){
          $photo_name="photo0".$photo_number.".jpg";
        }elsif($photo_number>=10 and $photo_number < 100){
          $photo_name="photo".$photo_number.".jpg";
        }
        move "$students_dir/$username/profile.jpg", "$students_dir/$username/$photo_name";
      }
    }
    open(OUTFILE, ">", "$students_dir/$username/profile.jpg") or die "Couldn't open $output_file for writing:$!";
    while($bytesread = read($file, $buffer, 1024)){
      print OUTFILE $buffer;
    }
    close OUTFILE;
    $msg.="$file was successfully uploaded.<br>"
  }
  my @imglist = ('img1', 'img2', 'img3', 'img4', 'img5');
  foreach my $img (@imglist){
    next if (param($img) eq "");
    my @uploaded_photos = glob("$students_dir/$username/photo*.jpg");
    my ($photo_name, $photo_number);
    $photo_number = $#uploaded_photos+1;
    print $photo_number;
    if($photo_number<10){
      $photo_name="photo0".$photo_number.".jpg";
    }elsif($photo_number>=10 and $photo_number < 100){
      $photo_name="photo".$photo_number.".jpg";
    }else{
      $msg.="<font color =\"red\">Maximum number of photos exceeded. ".param($img)." couldn't be uploaded.</font><br>";
    }
    my $file = param($img);
    my $username = param('user');
    my $output_file = "$students_dir/$username/$photo_name";
    my ($bytesread, $buffer);
    open(OUTFILE, ">", $output_file) or die "Couldn't open $output_file for writing:$!";
    while($bytesread = read($file, $buffer, 1024)){
      print OUTFILE $buffer;
    }
    close OUTFILE;
    $msg.=param($img)." has been successfully uploaded.<br>";
  }
  return p,
  $msg,
  upload_photos();
}

sub delete_photos(){
  my $username = param('user');
  my @photo_list = glob("$students_dir/$username/photo*.jpg");
  my $no_of_photos = $#photo_list;
  my $url = self_url;
  $url=~s/\/love2041\.cgi.*$//;
  $url.="/love2041.cgi?user=$username&menu=view+photos";
  unlink "$students_dir/$username/profile.jpg" if defined param('delete');
  if(defined param('delete selected photos')){
    foreach my $photo(reverse @photo_list){
      $photo =~ /$students_dir\/$username\/(.+)$/;
      my $photo_name = $1;
      if (defined param($photo_name)){
        $photo_name =~ /photo([0-9]{2})\.jpg/;
        my $photo_number = $1;
        $photo_number =~ s/^0//;
        unlink $photo;
        for (my $i = $photo_number+1; $i<=$no_of_photos+1; $i++){
          my $new_photo_no = $i-1;
          my $move_photo = $photo_list[$i];
          $new_photo_no = "0".$new_photo_no if $new_photo_no =~ m/^[0-9]$/;
          move "$move_photo", "$students_dir/$username/photo$new_photo_no.jpg";
          $no_of_photos -= 1;
        }
      }
    }
  }
  return "<meta http-equiv=\"refresh\" content=\"0; url=$url\" />";
}
sub view_student(){
  return message_write() if defined param('message');
  return view_student_photos() if defined param('view photos');
}

sub view_student_photos(){
  my $student = param('user_search');
  my $username = param('user');
  my @uploaded_photos = glob("$students_dir/$student/photo*.jpg");
  my $col = 0;
  my $profile_html='';
  my $photos_html ='';
  my $url = self_url;
  $url=~s/\/love2041\.cgi.*$//;
  $url.="/love2041.cgi?";
  if(-e "$students_dir/$student/profile.jpg"){
    $profile_html.="<img style = \"width:250px;\" src=\"$students_dir/$student/profile.jpg\">";
  }
  $photos_html.="<table><tr>";
  foreach my $photo (@uploaded_photos){
    $photo =~ /$students_dir\/$student\/(.+)$/;
    my $photo_name = $1;
    my $photo_url = $url."page=view_student_photo&photo=$photo_name&user=$username&user_search=$student";
    $photos_html .="<td><a href = \"$photo_url\"><img style = \"width: 250px;\" src = \"$photo\"></a><td>";
    if ($col == 2){
      $col = 0;
      $photos_html.="</tr><tr>";
    }else{
      $col+=1;
    }
  }
  $photos_html.="</table>";
  $photos_html = "" if $photos_html eq "<table><tr></table>";
  return p,
  h3("profile photo:"), "<br>",
  $profile_html,p,
  h3("photos:"),"<br>",
  $photos_html,
  end_form;
}
sub view_student_photo(){
  my $username = param('user');
  my $student = param('user_search');
  my $photo_name = param('photo');
  return p,
  "<img src =\"$students_dir/$student/$photo_name\">";
}
sub message_write(){
  my $username = param('user');
  my $user_msg = param('user_search');
  param('page', 'message_send');
  return p,
  start_form(),
  hidden('user'), hidden('user_search'), hidden('page'), hidden('email'),
  "Write your message:<br>", textarea('message', '', 20, 50), p,
  submit('send'),
  end_form;
}

sub message_send(){
  my $username = param('user');
  my $user_msg = param('user_search');
  my $msg = param('message');
  my $link = self_url;
  $link=~s/\/love2041\.cgi.*$//;
  my $email;
  my $profile_filename = "$students_dir/$user_msg/profile.txt";
  open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
  while(my $line = <$p>){
    if ($line =~ /^email:\s*$/){
      $line = <$p>;
      $line =~ /^\s*([^\s]+)\s*$/;
      $email = $1;
      last;
    }
  }
  close $p;
  $link .= "/love2041.cgi?page=message_write&user=$user_msg&user_search=$username";
  open MAIL, '|-','mail','-s',"LOVE2041 - Message from $username", $email or die "Can not run email";
  print MAIL "Message:\n$msg\n\n";
  print MAIL "Click the link to reply.\n$link\n";
  return p,
  "Message has been sent.";
}
#
# HTML placed at bottom of every screen
#
sub page_header {
	return header,
  start_html("-title"=>"LOVE2041", -style=>{-src=>['style.css']}),
  (h1({-align=>right},"LOVE2041"));
}

#
# HTML placed at bottom of every screen
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
  
	my $html = "";
	$html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
	$html .= end_html;
	return $html;
}


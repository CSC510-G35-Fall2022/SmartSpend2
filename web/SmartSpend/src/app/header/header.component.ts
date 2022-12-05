import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AppService } from '../app.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.css']
})
export class HeaderComponent {

  constructor(public appService: AppService, public router: Router, public route: ActivatedRoute) {}
home() {
  // this.router.navigate(['../', { id: this.appService.userId, }], { relativeTo: this.route });
  this.router.navigate(['../limits', ], { relativeTo: this.route });


}

}

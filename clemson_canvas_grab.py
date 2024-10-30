import argparse 
import canvas_grab 
from canvasapi import Canvas
from termcolor import colored
from canvasapi.exceptions import ResourceDoesNotExist
from canvas_grab.config import Config


class ClemsonCanvasGrab:
    def __init__(self, token, download_folder='files'):
        self.config = Config()
        self.config.endpoint.endpoint = "https://clemson.instructure.com/"
        self.config.endpoint.api_key = token 
        self.config.download_folder = download_folder
        self.config.file_filter.allowed_group = ['Document']
        self.config.organize_mode.mode = 'module_link'

        self.canvas = self.config.endpoint.login()
        self.courses = list(self.canvas.get_courses())
        self.available_courses, self.not_available = canvas_grab.utils.filter_available_courses(self.courses)
        self.filtered_courses = self.config.course_filter.get_filter().filter_course(self.available_courses)

        self.id_course_map = {course.id: course for course in self.courses}

    def get_course_names(self):
        return [course.name for course in self.filtered_courses]

    def get_course_by_id(self, course_id):
        return self.id_course_map.get(course_id, None)

    def update_local_course_info(self, course_id):
        course = self.get_course_by_id(course_id)
        assert course is not None, f'Course with id {course_id} not found'

        self.conduct_download(course)

    def conduct_download(self, course):
        config = self.config
        course_name_parser = canvas_grab.course_parser.CourseParser()
        # take on-disk snapshot
        parsed_name = course_name_parser.get_parsed_name(course)
        print(f'  Download to {colored(parsed_name, "cyan")}')
        on_disk_path = f'{config.download_folder}/{parsed_name}'
        print("On disk path: ", on_disk_path)

        on_disk_snapshot = canvas_grab.snapshot.OnDiskSnapshot(
            on_disk_path).take_snapshot()

        # take canvas snapshot
        mode, canvas_snapshots = config.organize_mode.get_snapshots(course)
        canvas_snapshot = {}
        for canvas_snapshot_obj in canvas_snapshots:
            try:
                canvas_snapshot = canvas_snapshot_obj.take_snapshot()
            except ResourceDoesNotExist:
                print(
                    colored(f'{mode} not supported, falling back to alternative mode', 'yellow'))
                continue
            break

        # generate transfer plan
        planner = canvas_grab.planner.Planner(config.organize_mode.delete_file)
        plans = planner.plan(
            canvas_snapshot, on_disk_snapshot, config.file_filter)
        print(colored(
            f'  Updating {len(plans)} objects ({len(canvas_snapshot)} remote objects -> {len(on_disk_snapshot)} local objects)'))
        # start download
        transfer = canvas_grab.transfer.Transfer()
        transfer.transfer(
            on_disk_path, f'{config.download_folder}/_canvas_grab_archive', plans)

    # for idx, course in enumerate(filtered_courses):
    #     course_name = course.name

def main(args):
    g = ClemsonCanvasGrab(args.token, args.save_path)

    if args.list_courses:
        print(g.get_course_names())
        return 
    
    if args.course_id is not None:
        g.update_local_course_info(args.course_id)

    


if __name__ == '__main__':
    # Add args for canvas token and course id
    parser = argparse.ArgumentParser(description='Grab files from Canvas')
    parser.add_argument('--token', type=str, help='Canvas API token', required=True)
    parser.add_argument('--list_courses', action='store_true', help='List course ids')
    parser.add_argument('--course_id', type=int, help='Canvas course id to download from', default=None)
    parser.add_argument('--save_path', type=str, help='Path to save/update downloaded files, will check the contents of this directory', default='.')

    args = parser.parse_args()
    main(args)
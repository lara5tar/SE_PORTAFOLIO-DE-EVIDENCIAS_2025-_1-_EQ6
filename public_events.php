<?php
defined('BASEPATH') OR exit('No direct script access allowed');

require_once(APPPATH . '/libraries/REST_Controller.php');
use Restserver\Libraries\REST_Controller;

class Events extends REST_Controller {

    public function __construct() {
        header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE");
        header("Access-Control-Allow-Headers: Content-Type, Content-Length, Accept-Encoding");
        header("Access-Control-Allow-Origin: *");

        parent::__construct();
        $this->load->database();
    }

    // Obtener todos los eventos
    public function index_get() {
        $query = $this->db->get('PUBLIC_EVENT');
        $events = $query->result_array();

        $response = array(
            'error' => FALSE,
            'events' => $events
        );

        $this->response($response);
    }

    // Obtener un evento por ID
    public function event_get($id) {
        $this->db->where('id', $id);
        $query = $this->db->get('PUBLIC_EVENT');
        $event = $query->row_array();

        if ($event) {
            $response = array(
                'error' => FALSE,
                'event' => $event
            );
        } else {
            $response = array(
                'error' => TRUE,
                'message' => 'Event not found'
            );
            $this->response($response, REST_Controller::HTTP_NOT_FOUND);
        }

        $this->response($response);
    }

    // Crear un nuevo evento
    public function index_post() {
        $data = $this->post();

        if (empty($data)) {
            $response = array(
                'error' => TRUE,
                'message' => 'No data provided'
            );
            $this->response($response, REST_Controller::HTTP_BAD_REQUEST);
            return;
        }

        $this->db->insert('PUBLIC_EVENT', $data);
        $id = $this->db->insert_id();

        $response = array(
            'error' => FALSE,
            'id' => $id,
            'message' => 'Event created successfully'
        );

        $this->response($response, REST_Controller::HTTP_CREATED);
    }

    // Actualizar un evento existente
    public function event_put($id) {
        $data = $this->put();

        if (empty($data)) {
            $response = array(
                'error' => TRUE,
                'message' => 'No data provided'
            );
            $this->response($response, REST_Controller::HTTP_BAD_REQUEST);
            return;
        }

        $this->db->where('id', $id);
        $this->db->update('PUBLIC_EVENT', $data);

        $response = array(
            'error' => FALSE,
            'message' => 'Event updated successfully'
        );

        $this->response($response);
    }

    // Eliminar un evento
    public function event_delete($id) {
        $this->db->where('id', $id);
        $this->db->delete('PUBLIC_EVENT');

        $response = array(
            'error' => FALSE,
            'message' => 'Event deleted successfully'
        );

        $this->response($response);
    }
}